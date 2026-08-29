from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Request, BackgroundTasks
from chat_engine.db import get_conn
from core.time_context import build_time_context, build_llm_time_hint
from core.askyellow_context import get_relevant_askyellow_context
from core.mhjh_context import get_relevant_mhjh_context
from core.capability_router import detect_capability

import hashlib
import hmac
import json
import os
import time

from chat_shared import (
    store_message_pair,
    get_user_history,
    get_auth_user_from_session,
    build_welcome_message,
    get_history_for_llm,
    get_available_history_days,
    get_user_history_by_day,
    get_user_images,
)

from image_shared import (
    generate_image,
    analyze_uploaded_image,
    edit_uploaded_image,
    detect_uploaded_image_operation,
    read_and_validate_upload,
)

from llm import call_yellowmind_llm, call_gabber_yello_llm
from gabber_web import format_web_context, search_web_for_gabber, should_search_web
from gabber_memory import (
    clear_gabber_memories,
    format_gabber_memories,
    get_gabber_memories,
    learn_gabber_memories,
)
from music_recognition import (
    MAX_UPLOAD_BYTES,
    MusicRecognitionError,
    check_music_rate_limit,
    recognize_music,
)

router = APIRouter()

TIME_CONTEXT_TRIGGERS = (
    "vandaag", "gisteren", "morgen", "datum", "tijd", "hoe laat",
    "welke dag", "deze week", "vorige week", "volgende week",
    "dit jaar", "vorig jaar", "volgend jaar", "recent", "actueel",
    "momenteel", "nu", "jaarwisseling",
)


def _needs_time_context(text: str) -> bool:
    q = (text or "").lower()
    return any(trigger in q for trigger in TIME_CONTEXT_TRIGGERS)


def _gabber_test_session_id(session_id: str) -> str:
    """Keep Gabber Yello test history isolated from YellowMind history."""
    return f"gabber-yello-test:{session_id}"


def _is_memory_question(text: str) -> bool:
    q = " ".join((text or "").lower().split())
    patterns = (
        "wat onthoud je over mij", "wat weet je over mij",
        "wat heb je over mij onthouden", "ken je mij al een beetje",
    )
    return any(pattern in q for pattern in patterns)


def _is_forget_all_request(text: str) -> bool:
    q = " ".join((text or "").lower().split())
    patterns = (
        "vergeet alles wat je over mij weet",
        "vergeet alles wat je over mij onthoudt",
        "wis mijn geheugen",
        "verwijder mijn herinneringen",
    )
    return any(pattern in q for pattern in patterns)


def _is_identity_question(text: str) -> bool:
    q = " ".join((text or "").lower().split())
    patterns = (
        "wie ben ik", "weet je wie ik ben", "ken je mij", "herken je mij",
        "met wie praat je", "met wie chat je", "weet je mijn naam",
        "hoe heet ik", "wat is mijn naam",
    )
    return any(pattern in q for pattern in patterns)


def _verified_mhjh_member(request: Request, payload: dict) -> dict | None:
    """Verify the minimal MijnMHJH identity forwarded by the MHJH server."""
    context_json = payload.get("member_context")
    timestamp = request.headers.get("x-mhjh-timestamp", "")
    supplied = request.headers.get("x-mhjh-signature", "")
    secret = os.getenv("GABBER_YELLO_BRIDGE_SECRET", "").strip()

    def reject(reason: str) -> None:
        print("GABBER_MEMBER_AUTH_REJECT " + json.dumps({
            "event": "GABBER_MEMBER_AUTH_REJECT",
            "reason": reason,
            "has_context": isinstance(context_json, str),
            "context_bytes": len(context_json.encode("utf-8")) if isinstance(context_json, str) else 0,
            "has_timestamp": bool(timestamp),
            "has_signature": bool(supplied),
            "secret_configured": len(secret) >= 32,
            "secret_fingerprint": hashlib.sha256(secret.encode("utf-8")).hexdigest()[:12] if secret else "",
        }, separators=(",", ":")), flush=True)

    if not isinstance(context_json, str):
        reject("context_missing")
        return None
    if not timestamp:
        reject("timestamp_missing")
        return None
    if not supplied:
        reject("signature_missing")
        return None
    if len(secret) < 32:
        reject("secret_missing_or_short")
        return None

    try:
        issued_at = int(timestamp)
    except (TypeError, ValueError):
        reject("timestamp_invalid")
        return None

    if abs(int(time.time()) - issued_at) > 300:
        reject("timestamp_expired")
        return None

    expected = hmac.new(
        secret.encode("utf-8"),
        f"{timestamp}.{context_json}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, supplied):
        reject("signature_mismatch")
        return None

    try:
        member = json.loads(context_json)
    except (TypeError, ValueError, json.JSONDecodeError):
        reject("context_invalid_json")
        return None

    if not isinstance(member, dict):
        reject("context_not_object")
        return None
    if not member.get("public_id"):
        reject("public_id_missing")
        return None

    return {
        "public_id": str(member["public_id"])[:80],
        "first_name": str(member.get("first_name") or "").strip()[:80],
        "nickname": str(member.get("nickname") or "").strip()[:80],
    }


def _gabber_conversation_session(member: dict | None, browser_session_id: str) -> str:
    if not member:
        return _gabber_test_session_id(browser_session_id)

    secret = os.getenv("GABBER_YELLO_BRIDGE_SECRET", "").strip()
    digest = hmac.new(
        secret.encode("utf-8"),
        member["public_id"].encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"gabber-yello-member:{digest}"


@router.post("/gabber-yello/recognize-music")
def gabber_yello_recognize_music(
    request: Request,
    member_context: str = Form(...),
    file: UploadFile = File(...),
):
    member = _verified_mhjh_member(request, {"member_context": member_context})
    if not member:
        raise HTTPException(status_code=401, detail="member_required")

    content_type = (file.content_type or "").lower()
    audio_bytes = file.file.read(MAX_UPLOAD_BYTES + 1)
    file.file.close()
    if not audio_bytes or len(audio_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="audio_too_large")

    if not check_music_rate_limit(member["public_id"]):
        raise HTTPException(status_code=429, detail="music_rate_limit")

    try:
        result = recognize_music(
            member_public_id=member["public_id"],
            filename=file.filename or "fragment",
            content_type=content_type,
            audio_bytes=audio_bytes,
        )
    except MusicRecognitionError as exc:
        code = str(exc)
        status = 503 if code in {"audd_not_configured", "provider_unavailable"} else 422
        raise HTTPException(status_code=status, detail=code) from exc

    if not result.get("matched"):
        return {
            "matched": False,
            "reply": (
                "Ik krijg hier geen betrouwbare herkenning uit, maat. "
                "Het kan een live-edit, mash-up of te kort fragment zijn."
            ),
        }

    artist = result["artist"]
    title = result["title"]
    return {
        **result,
        "reply": (
            f"Maat, dit lijkt op {artist} – {title} 🔥 "
            "Bij een live-edit, remix of mash-up kan dit wel de oorspronkelijke track zijn."
        ),
    }


@router.get("/chat/history")
def chat_history(session_id: str, day: str | None = Query(default=None)):
    conn = get_conn()
    try:
        user = get_auth_user_from_session(conn, session_id)

        if not user:
            return {
                "available_days": [],
                "messages": [],
                "today": [],
                "yesterday": [],
                "welcome": None,
            }

        user_id = user["id"]
        first_name = user.get("first_name")

        if day == "list":
            return {
                "available_days": get_available_history_days(conn, user_id)
            }

        if day == "images":
            return {
                "images": get_user_images(conn, user_id)
            }

        if day and day not in ("today", "yesterday"):
            messages = get_user_history_by_day(conn, user_id, day)
            return {
                "day": day,
                "messages": messages,
                "available_days": get_available_history_days(conn, user_id),
            }

        today_messages = get_user_history(conn, user_id, "today")
        yesterday_messages = get_user_history(conn, user_id, "yesterday")

        return {
            "available_days": get_available_history_days(conn, user_id),
            "today": today_messages,
            "yesterday": yesterday_messages,
            "welcome": build_welcome_message(first_name),
        }
    finally:
        conn.close()


@router.post("/chat")
def chat(payload: dict):
    session_id = payload.get("session_id")
    message = payload.get("message", "").strip()
    wants_image = payload.get("wants_image", False)

    if not session_id or not message:
        raise HTTPException(status_code=400, detail="session_id of message ontbreekt")

    # Capability routing stays cheap and deterministic. The cold Shopper owns
    # actionable product-search requests; YellowMind owns normal conversation.
    if not wants_image and detect_capability(message) == "shopper":
        return {
            "type": "search",
            "query": message,
            "capability": "shopper",
        }

    conn = get_conn()
    try:
        history = get_history_for_llm(conn, session_id)
        user = get_auth_user_from_session(conn, session_id)
    finally:
        conn.close()

    hints = {}

    if user and user.get("first_name"):
        hints["user_name"] = user["first_name"]

    if _needs_time_context(message):
        hints["time_context"] = build_time_context()
        hints["time_hint"] = build_llm_time_hint()

    if wants_image:
        image_url = generate_image(message)

        if not image_url:
            raise HTTPException(status_code=500, detail="Afbeelding genereren mislukt")

        store_message_pair(session_id, message, "[IMAGE]" + image_url)
        return {
            "type": "image",
            "url": image_url
        }

    kb_answer = get_relevant_askyellow_context(message)

    answer, _ = call_yellowmind_llm(
        question=message,
        language="nl",
        kb_answer=kb_answer,
        sql_match=None,
        hints=hints,
        history=history
    )

    if not answer:
        answer = "⚠️ Ik kreeg geen inhoudelijk antwoord terug."

    store_message_pair(session_id, message, answer)
    return {"reply": answer}


@router.post("/gabber-yello/chat")
def gabber_yello_chat(payload: dict, request: Request, background_tasks: BackgroundTasks):
    """Private staging test route for Gabber Yello.

    Uses the same Yello Core and database-backed memory functions as YellowMind,
    but stores history under an isolated test session id so the personalities do
    not contaminate each other's conversations.
    """
    session_id = (payload.get("session_id") or "").strip()
    message = (payload.get("message") or "").strip()

    if not session_id or not message:
        raise HTTPException(status_code=400, detail="session_id of message ontbreekt")

    member = _verified_mhjh_member(request, payload)
    conversation_session = _gabber_conversation_session(member, session_id)

    conn = get_conn()
    try:
        history = get_history_for_llm(conn, conversation_session)
    finally:
        conn.close()

    hints = {}
    member_memories = []
    if member:
        display_name = member["nickname"] or member["first_name"]
        if display_name:
            hints["user_name"] = display_name
        try:
            member_memories = get_gabber_memories(conversation_session)
            memory_context = format_gabber_memories(member_memories)
            if memory_context:
                hints["personal_memory"] = memory_context
        except Exception as exc:
            print(f"Gabber Yello memory loading failed: {type(exc).__name__}: {exc}")

    if _needs_time_context(message):
        hints["time_context"] = build_time_context()
        hints["time_hint"] = build_llm_time_hint()

    if _is_forget_all_request(message):
        if member:
            clear_gabber_memories(conversation_session)
            answer = "Is goed maat — mijn persoonlijke herinneringen over jou zijn gewist."
        else:
            answer = "Je bent niet ingelogd maat, dus ik heb geen accountgeheugen om te wissen."
        store_message_pair(conversation_session, message, answer)
        return {
            "reply": answer,
            "personality": "gabber_yello",
            "knowledge_used": False,
            "memory_used": False,
            "member_recognized": bool(member),
        }

    if _is_memory_question(message):
        if member_memories:
            facts = "\n".join(f"- {item['value']}" for item in member_memories)
            answer = f"Dit heb ik van onze gesprekken onthouden, maat:\n{facts}"
        elif member:
            answer = "Nog niet veel maat — we zijn elkaar nog aan het leren kennen 😎"
        else:
            answer = "Je bent niet ingelogd via MijnMHJH, dus ik heb geen persoonlijk accountgeheugen voor je."
        store_message_pair(conversation_session, message, answer)
        return {
            "reply": answer,
            "personality": "gabber_yello",
            "knowledge_used": False,
            "memory_used": bool(member_memories),
            "member_recognized": bool(member),
        }

    if _is_identity_question(message):
        if member:
            display_name = member["nickname"] or member["first_name"]
            answer = (
                f"Jazeker maat! Jij bent {display_name} 😎 "
                "Je bent ingelogd via MijnMHJH, dus ik weet met wie ik sta te ouwehoeren."
            )
        else:
            answer = (
                "Nog niet maat — je bent hier niet ingelogd via MijnMHJH. "
                "Log daar ff in, dan weet ik met wie ik sta te ouwehoeren 😎"
            )
        store_message_pair(conversation_session, message, answer)
        return {
            "reply": answer,
            "personality": "gabber_yello",
            "knowledge_used": False,
            "member_recognized": bool(member),
        }

    mhjh_context = get_relevant_mhjh_context(message)
    if not mhjh_context and history:
        recent_user_context = [
            item["content"]
            for item in history[-8:]
            if item.get("role") == "user" and isinstance(item.get("content"), str)
        ]
        if recent_user_context:
            mhjh_context = get_relevant_mhjh_context(
                "\n".join(recent_user_context + [message])
            )

    web_results = []
    if should_search_web(message, bool(mhjh_context)):
        try:
            web_results = search_web_for_gabber(message)
            web_context = format_web_context(web_results)
            hints["web_search_succeeded"] = bool(web_results)
            hints["web_context"] = web_context or (
                "De internetzoekopdracht leverde geen bruikbare resultaten op. "
                "Zeg eerlijk dat je online niets betrouwbaars hebt gevonden."
            )
        except Exception as exc:
            print(f"Gabber Yello web search failed: {type(exc).__name__}: {exc}")
            hints["web_search_succeeded"] = False
            hints["web_context"] = (
                "De internetzoekopdracht is mislukt. Zeg kort dat online zoeken nu niet lukte "
                "en verzin geen actuele informatie."
            )

    try:
        answer, _ = call_gabber_yello_llm(
            question=message,
            language="nl",
            kb_answer=mhjh_context,
            sql_match=None,
            hints=hints,
            history=history,
        )
    except Exception as exc:
        print(f"Gabber Yello model call failed: {type(exc).__name__}: {exc}")
        answer = "Ik liep ff vast maat, maar ik ben er nog. Gooi 'm nog een keer!"

    if not answer:
        answer = "⚠️ Gabber Yello had ff een vastlopertje. Vraag het nog eens."

    if web_results:
        source_lines = [
            f"[{index}] {item['title']} — {item['url']}"
            for index, item in enumerate(web_results, start=1)
        ]
        answer = f"{answer}\n\nBronnen:\n" + "\n".join(source_lines)

    store_message_pair(conversation_session, message, answer)
    if member:
        background_tasks.add_task(
            learn_gabber_memories,
            conversation_session,
            message,
        )
    return {
        "reply": answer,
        "personality": "gabber_yello",
        "knowledge_used": bool(mhjh_context),
        "memory_used": bool(hints.get("personal_memory")),
        "web_used": bool(web_results),
        "sources": [
            {"title": item["title"], "url": item["url"]}
            for item in web_results
        ],
        "member_recognized": bool(member),
    }


@router.post("/gabber-yello/history")
def gabber_yello_history(payload: dict, request: Request):
    session_id = (payload.get("session_id") or "").strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id ontbreekt")

    member = _verified_mhjh_member(request, payload)
    if not member:
        return {"messages": [], "member_recognized": False}

    conversation_session = _gabber_conversation_session(member, session_id)
    conn = get_conn()
    try:
        messages = get_history_for_llm(conn, conversation_session, limit=30)
    finally:
        conn.close()

    return {
        "messages": messages,
        "member_recognized": True,
    }


@router.post("/gabber-yello/reset")
def reset_gabber_yello(payload: dict, request: Request):
    session_id = (payload.get("session_id") or "").strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id ontbreekt")

    member = _verified_mhjh_member(request, payload)
    conversation_session = _gabber_conversation_session(member, session_id)
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE conversations
            SET ended_at = NOW()
            WHERE session_id = %s
              AND ended_at IS NULL
            """,
            (conversation_session,)
        )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}


@router.post("/chat/image")
async def chat_with_uploaded_image(
    session_id: str = Form(...),
    message: str = Form(""),
    file: UploadFile = File(...),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id ontbreekt")

    image_bytes, mime_type = await read_and_validate_upload(file)

    conn = get_conn()
    try:
        history = get_history_for_llm(conn, session_id)
    finally:
        conn.close()

    operation = detect_uploaded_image_operation(message)
    user_log_text = f"[USER_IMAGE]{message or 'uploaded image'}"

    if operation == "edit":
        prompt = (message or "").strip() or "Maak van deze afbeelding een nette karikatuur."

        image_src = edit_uploaded_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
        )

        store_message_pair(session_id, user_log_text, f"[IMAGE]{image_src}")
        return {
            "type": "image",
            "mode": "edit",
            "url": image_src,
            "reply": "Hier is je bewerkte afbeelding."
        }

    answer = analyze_uploaded_image(
        image_bytes=image_bytes,
        mime_type=mime_type,
        question=message,
        history=history,
    )

    store_message_pair(session_id, user_log_text, answer)
    return {
        "type": "vision",
        "mode": "analyze",
        "reply": answer,
    }


@router.post("/chat/reset")
def reset_chat(payload: dict):
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400)

    conn = get_conn()
    try:
        user = get_auth_user_from_session(conn, session_id)
        cur = conn.cursor()

        if user:
            cur.execute(
                """
                UPDATE conversations
                SET ended_at = NOW()
                WHERE user_id = %s
                  AND ended_at IS NULL
                """,
                (user["id"],)
            )
        else:
            cur.execute(
                """
                UPDATE conversations
                SET ended_at = NOW()
                WHERE session_id = %s
                  AND ended_at IS NULL
                """,
                (session_id,)
            )

        conn.commit()
    finally:
        conn.close()

    return {"ok": True}
