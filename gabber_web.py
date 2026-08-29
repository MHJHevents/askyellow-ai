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
    "huidige agenda", "aankomende optredens", "treedt op", "treed op",
    "wanneer is het", "wanneer vindt", "is er nog", "bestaat nog",
)

# Only factual misses get an automatic internet fallback. Personal memories,
# opinions and casual conversation must stay a conversation instead of turning
# every message into a Google query.
_FACTUAL_QUESTION = re.compile(
    r"^(?:weet (?:je|jij)\s+)?(?:"
    r"wat (?:is|was|betekent)|wanneer|"
    r"waar (?:is|was|staat|ligt|vindt|speelt|draait)|welke (?:artiest|dj|track|plaat|versie|editie|datum)|"
    r"door wie|van wie|hoeveel|hoe heet|klopt het dat"
    r")\b",
    re.IGNORECASE,
)
_SCENE_FACT = re.compile(
    r"\b(track|plaat|nummer|release|remix|mashup|artiest|dj|liveact|label|"
    r"feest|festival|hardcorefestival|club|locatie|line-?up|optreden|editie|hardcore|gabber|hardstyle)\b",
    re.IGNORECASE,
)
_PERSONAL_OR_OPINION = re.compile(
    r"\b(ik vind|vind jij|volgens jou|favoriet|mijn herinnering|weet je nog|"
    r"wat denk je|hoe voel|anekdote|verhaal van mij|bij ons|onze familie)\b",
    re.IGNORECASE,
)
_SHORT_UNKNOWN_PERSON = re.compile(
    r"^(?:weet (?:je|jij)\s+)?wie (?:is|was)\s+[\w.'’-]+(?:\s+[\w.'’-]+){0,2}\??$",
    re.IGNORECASE,
)


def should_search_web(message: str, has_official_mhjh_context: bool) -> bool:
    q = " ".join((message or "").strip().split())
    q_lower = q.lower()

    # A direct request always wins, even when MHJH knowledge is available.
    if any(trigger in q_lower for trigger in _EXPLICIT) or _INTERNET_REQUEST.search(q):
        return True

    # Reviewed MHJH knowledge remains the primary source.
    if has_official_mhjh_context:
        return False

    if _PERSONAL_OR_OPINION.search(q):
        return False

    # A bare nickname/name is ambiguous: ask for context once instead of
    # searching the wrong person (for example: "Wie is Dof?").
    if _SHORT_UNKNOWN_PERSON.fullmatch(q):
        return False

    if any(trigger in q_lower for trigger in _CURRENT):
        return True

    # Automatic emergency exit for a sufficiently specific factual scene
    # question for which our reviewed knowledge returned no match.
    return bool(
        len(q.split()) >= 5
        and _FACTUAL_QUESTION.search(q)
        and _SCENE_FACT.search(q)
    )


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
