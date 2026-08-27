"""Structured OpenAI token logging for Render.

Every model call emits one compact JSON line. Render keeps stdout/stderr logs,
so usage can be filtered with ``AI_TOKEN_USAGE`` without storing prompts or
other personal content.
"""

import json
from datetime import datetime, timezone


def log_ai_token_usage(response, *, feature: str, model: str | None = None) -> dict:
    usage = getattr(response, "usage", None)
    prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", 0) or 0)

    cached_tokens = 0
    prompt_details = getattr(usage, "prompt_tokens_details", None)
    if prompt_details is not None:
        cached_tokens = int(getattr(prompt_details, "cached_tokens", 0) or 0)

    payload = {
        "event": "AI_TOKEN_USAGE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "feature": feature,
        "model": model or getattr(response, "model", None) or "unknown",
        "input_tokens": prompt_tokens,
        "cached_input_tokens": cached_tokens,
        "output_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }
    print("AI_TOKEN_USAGE " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")), flush=True)
    return payload
