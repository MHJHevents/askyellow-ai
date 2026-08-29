"""AudD music recognition for authenticated Gabber Yello members."""

from collections import defaultdict, deque
from datetime import datetime, timezone
import hashlib
import json
import os
import threading
import time

import requests


AUDD_ENDPOINT = "https://api.audd.io/"
MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_REQUESTS_PER_HOUR = 5
ALLOWED_MIME_TYPES = {
    "audio/mpeg", "audio/mp3", "audio/mp4", "audio/x-m4a", "audio/m4a",
    "audio/wav", "audio/x-wav", "audio/webm", "audio/ogg", "audio/flac",
    "video/mp4", "video/webm", "video/quicktime",
}

_rate_lock = threading.Lock()
_rate_events: dict[str, deque[float]] = defaultdict(deque)


class MusicRecognitionError(RuntimeError):
    pass


def check_music_rate_limit(member_public_id: str) -> bool:
    now = time.time()
    cutoff = now - 3600
    key = hashlib.sha256(member_public_id.encode("utf-8")).hexdigest()
    with _rate_lock:
        events = _rate_events[key]
        while events and events[0] < cutoff:
            events.popleft()
        if len(events) >= MAX_REQUESTS_PER_HOUR:
            return False
        events.append(now)
    return True


def _usage_log(member_public_id: str, *, matched: bool, size: int, status: str) -> None:
    member_hash = hashlib.sha256(member_public_id.encode("utf-8")).hexdigest()[:16]
    print("MUSIC_RECOGNITION_USAGE " + json.dumps({
        "event": "MUSIC_RECOGNITION_USAGE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "feature": "gabber_yello:music_recognition",
        "provider": "audd",
        "member_hash": member_hash,
        "matched": matched,
        "upload_bytes": size,
        "status": status,
    }, ensure_ascii=False, separators=(",", ":")), flush=True)


def recognize_music(
    *,
    member_public_id: str,
    filename: str,
    content_type: str,
    audio_bytes: bytes,
) -> dict:
    token = os.getenv("AUDD_API_TOKEN", "").strip()
    if not token:
        raise MusicRecognitionError("audd_not_configured")
    if not audio_bytes or len(audio_bytes) > MAX_UPLOAD_BYTES:
        raise MusicRecognitionError("invalid_file_size")

    mime = (content_type or "").lower().split(";", 1)[0].strip()
    if mime not in ALLOWED_MIME_TYPES:
        raise MusicRecognitionError("unsupported_media_type")

    safe_name = os.path.basename(filename or "fragment.bin")[:180]
    try:
        response = requests.post(
            AUDD_ENDPOINT,
            data={
                "api_token": token,
                "return": "apple_music,spotify",
            },
            files={"file": (safe_name, audio_bytes, mime)},
            timeout=(8, 30),
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        _usage_log(member_public_id, matched=False, size=len(audio_bytes), status="provider_error")
        raise MusicRecognitionError("provider_unavailable") from exc

    if payload.get("status") != "success":
        provider_error = payload.get("error") if isinstance(payload.get("error"), dict) else {}
        error_code = str(provider_error.get("error_code") or payload.get("error_code") or "")[:80]
        error_message = str(
            provider_error.get("error_message")
            or provider_error.get("message")
            or payload.get("error_message")
            or payload.get("message")
            or ""
        ).strip()[:300]
        print("MUSIC_RECOGNITION_PROVIDER_ERROR " + json.dumps({
            "event": "MUSIC_RECOGNITION_PROVIDER_ERROR",
            "provider": "audd",
            "error_code": error_code,
            "error_message": error_message,
            "mime": mime,
            "filename_extension": os.path.splitext(safe_name)[1].lower()[:12],
        }, ensure_ascii=False, separators=(",", ":")), flush=True)
        _usage_log(member_public_id, matched=False, size=len(audio_bytes), status="provider_rejected")
        raise MusicRecognitionError("provider_rejected")

    result = payload.get("result")
    if not isinstance(result, dict):
        _usage_log(member_public_id, matched=False, size=len(audio_bytes), status="no_match")
        return {"matched": False}

    artist = str(result.get("artist") or "").strip()[:200]
    title = str(result.get("title") or "").strip()[:250]
    if not artist or not title:
        _usage_log(member_public_id, matched=False, size=len(audio_bytes), status="no_match")
        return {"matched": False}

    spotify = result.get("spotify") if isinstance(result.get("spotify"), dict) else {}
    apple = result.get("apple_music") if isinstance(result.get("apple_music"), dict) else {}
    _usage_log(member_public_id, matched=True, size=len(audio_bytes), status="matched")
    return {
        "matched": True,
        "artist": artist,
        "title": title,
        "album": str(result.get("album") or "").strip()[:250] or None,
        "release_date": str(result.get("release_date") or "").strip()[:40] or None,
        "label": str(result.get("label") or "").strip()[:200] or None,
        "spotify_url": str((spotify.get("external_urls") or {}).get("spotify") or "").strip() or None,
        "apple_music_url": str(apple.get("url") or "").strip() or None,
    }
