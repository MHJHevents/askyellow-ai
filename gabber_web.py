"""Guarded web-search routing for Gabber Yello."""

import re

from websearch import do_websearch


_EXPLICIT = (
    "zoek op internet", "zoek eens op", "zoek dit op", "google dit",
    "kun je dit opzoeken", "kun je online zoeken", "check online",
)
_INTERNET_REQUEST = re.compile(
    r"\b(zoek(?:en)?|vind(?:en)?|opzoek(?:en)?|check(?:en)?)\b.{0,45}\b(internet|online|web)\b"
    r"|\b(internet|online|web)\b.{0,45}\b(zoek(?:en)?|vind(?:en)?|opzoek(?:en)?|check(?:en)?)\b",
    re.IGNORECASE,
)

_CURRENT = (
    "laatste nieuws", "nieuwste nieuws", "meest recente", "actueel",
    "vandaag bekend", "deze week bekend", "net bekendgemaakt",
    "huidige agenda", "aankomende optredens",
)


def should_search_web(message: str, has_official_mhjh_context: bool) -> bool:
    q = " ".join((message or "").lower().split())
    if any(trigger in q for trigger in _EXPLICIT) or _INTERNET_REQUEST.search(q):
        return True
    if has_official_mhjh_context:
        return False
    return any(trigger in q for trigger in _CURRENT)


def search_web_for_gabber(message: str, limit: int = 4) -> list[dict]:
    query = " ".join((message or "").split())[:300]
    if len(query) < 8:
        return []

    results = do_websearch(query)
    cleaned = []
    for item in results[:limit]:
        title = " ".join(str(item.get("title") or "").split())[:180]
        snippet = " ".join(str(item.get("snippet") or "").split())[:500]
        url = str(item.get("url") or "").strip()
        if not title or not url or not re.match(r"^https?://", url, re.IGNORECASE):
            continue
        cleaned.append({"title": title, "snippet": snippet, "url": url})
    return cleaned


def format_web_context(results: list[dict]) -> str | None:
    if not results:
        return None
    parts = []
    for index, item in enumerate(results, start=1):
        parts.append(
            f"[{index}] {item['title']}\n"
            f"{item['snippet']}\n"
            f"URL: {item['url']}"
        )
    return "\n\n".join(parts)
