"""Safe, account-bound long-term memory for Gabber Yello."""

import json
import os
import re

from openai import OpenAI

from chat_engine.db import get_conn
from token_usage import log_ai_token_usage


_MODEL = os.getenv("GABBER_MEMORY_MODEL", "gpt-4o-mini")
_CANDIDATE = re.compile(
    r"\b(ik ben|ik heb|ik vind|ik hou|ik ga al|mijn |voor mij|favoriet|herinnering|carriere)\b",
    re.IGNORECASE,
)
_KEY = re.compile(r"^[a-z0-9_]{3,64}$")


def get_gabber_memories(member_key: str, limit: int = 10) -> list[dict]:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT fact_key, fact_value
            FROM gabber_yello_memories
            WHERE member_key = %s
            ORDER BY updated_at DESC, id DESC
            LIMIT %s
            """,
            (member_key, limit),
        )
        return [{"key": row["fact_key"], "value": row["fact_value"]} for row in cur.fetchall()]
    finally:
        conn.close()


def format_gabber_memories(memories: list[dict]) -> str | None:
    if not memories:
        return None
    return "\n".join(f"- {item['value']}" for item in memories)


def clear_gabber_memories(member_key: str) -> int:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM gabber_yello_memories WHERE member_key = %s", (member_key,))
        deleted = cur.rowcount
        conn.commit()
        return deleted
    finally:
        conn.close()


def learn_gabber_memories(member_key: str, user_text: str) -> None:
    """Extract at most two explicit, non-sensitive durable facts in the background."""
    text = " ".join((user_text or "").split())
    if len(text) < 20 or not _CANDIDATE.search(text):
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return

    try:
        client = OpenAI(api_key=api_key)
        result = client.chat.completions.create(
            model=_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Haal uit één Nederlands chatbericht maximaal twee expliciet vertelde, bruikbare "
                        "langetermijnherinneringen over de gebruiker. Bewaar alleen stabiele voorkeuren, "
                        "achtergrond, betekenisvolle ervaringen of doorlopende doelen. Bewaar nooit "
                        "gezondheid, middelengebruik, seksualiteit, religie, politiek, financiën, juridische "
                        "zaken, exacte locatie, contactgegevens, beveiligingsgegevens, tijdelijke stemming, "
                        "MijnMHJH-identiteit of officiële MHJH-feiten. Verzin en interpreteer niets. "
                        "Geef JSON: {\"memories\":[{\"key\":\"snake_case\",\"value\":\"korte feitelijke zin\"}]} ."
                    ),
                },
                {"role": "user", "content": text[:1200]},
            ],
        )
        log_ai_token_usage(result, feature="memory:gabber_yello", model=_MODEL)
        content = result.choices[0].message.content if result.choices else ""
        payload = json.loads(content or "{}")
        memories = payload.get("memories", [])
        if not isinstance(memories, list):
            return

        cleaned = []
        for item in memories[:2]:
            if not isinstance(item, dict):
                continue
            key = str(item.get("key") or "").strip().lower()
            value = " ".join(str(item.get("value") or "").split())[:300]
            if _KEY.fullmatch(key) and 5 <= len(value) <= 300:
                cleaned.append((key, value, text[:500]))

        if not cleaned:
            return

        conn = get_conn()
        try:
            cur = conn.cursor()
            for key, value, source in cleaned:
                cur.execute(
                    """
                    INSERT INTO gabber_yello_memories(member_key, fact_key, fact_value, source_text)
                    VALUES(%s, %s, %s, %s)
                    ON CONFLICT(member_key, fact_key)
                    DO UPDATE SET fact_value=EXCLUDED.fact_value,
                                  source_text=EXCLUDED.source_text,
                                  updated_at=NOW()
                    """,
                    (member_key, key, value, source),
                )
            conn.commit()
        finally:
            conn.close()
    except Exception as exc:
        print(f"Gabber Yello memory learning failed: {type(exc).__name__}: {exc}")
