"""Guarded web-search routing for Gabber Yello."""

import re
from urllib.parse import urlparse

from gabber_context import is_current_gabber_question, resolve_gabber_context

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
    "dit weekend", "komend weekend", "aankomend weekend", "volgend weekend",
    "aankomende feesten", "komende feesten", "feestjes dit weekend", "feesten dit weekend",
    "nog steeds", "dit jaar", "volgend jaar", "gaat het door", "gaat dat door", "actuele status",
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

    # Personal opinions and memories stay conversational.
    if _PERSONAL_OR_OPINION.search(q):
        return False

    # Current/recent questions always require a fresh web check, even when
    # reviewed MHJH knowledge also contains an older fact about the subject.
    if any(trigger in q_lower for trigger in _CURRENT) or is_current_gabber_question(q):
        return True

    # Reviewed MHJH knowledge remains the primary source for historical facts.
    if has_official_mhjh_context:
        return False

    # A bare nickname/name is ambiguous: ask for context once instead of
    # searching the wrong person (for example: "Wie is Dof?").
    if _SHORT_UNKNOWN_PERSON.fullmatch(q):
        return False

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


_SOURCE_STOPWORDS = {
    "wat", "wie", "waar", "wanneer", "waarom", "welke", "hoe", "dat", "dit",
    "die", "het", "een", "van", "voor", "met", "naar", "over", "zijn", "was",
    "wordt", "worden", "heeft", "hebben", "kan", "kun", "kunnen", "nog", "steeds",
    "ook", "dus", "maar", "dan", "wel", "niet", "geen", "weet", "zeker", "huhhh",
    "zoek", "zoeken", "eens", "even", "ditmaal", "internet", "online", "web", "check",
    "opzoeken", "google", "vertel", "mij", "maat", "maatje", "actuele", "actueel",
    "status", "huidige", "jaar", "editie", "festival", "feest", "hardcore", "gabber",
    "artiest", "track", "plaat", "nummer", "release", "nieuwste", "laatste", "recentste",
    "camping", "campsite", "line", "up", "lineup", "tickets", "kaartjes", "datum",
}
_STATUS_LOOKUP = re.compile(r"\b(?:actuele status|nog steeds|bestaat|terugkeer)\b", re.IGNORECASE)
_CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
UNCONFIRMED_WEB_REPLY = "Ik kan dit met de gevonden bronnen niet betrouwbaar bevestigen, maat."


def _plain(text):
    from core.mhjh_context import _normalize
    return _normalize(text)


def _subject_supported(subject, text):
    normalized = " " + _plain(text) + " "
    name = _plain(subject)
    variants = {name, re.sub(r"^(?:the|dj)\s+", "", name)}
    return any(value and " " + value + " " in normalized for value in variants)


def filter_gabber_web_results(results, query, subjects=(), limit=4):
    """A relevance gate on search metadata, not a claim of full-page verification."""
    anchors = {
        token for token in _plain(query).split()
        if len(token) >= 3 and token not in _SOURCE_STOPWORDS and not token.isdigit()
    }
    if not subjects and not anchors:
        return []
    years = {int(value) for value in re.findall(r"\b(?:19|20)\d{2}\b", query or "")}
    status_lookup = bool(_STATUS_LOOKUP.search(query or ""))
    camping_lookup = bool(re.search(r"\b(?:camping|campsite|kamperen)\b", query or "", re.IGNORECASE))
    kept, seen = [], set()
    for item in results or []:
        title = str(item.get("title") or "").strip()
        snippet = str(item.get("snippet") or "").strip()
        url = str(item.get("url") or "").strip()
        parsed = urlparse(url)
        if not title or parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            continue
        if url in seen:
            continue
        # A topic in an arbitrary URL is not evidence that its contents support it.
        text = title + " " + snippet
        if subjects:
            if not any(_subject_supported(subject, text) for subject in subjects):
                continue
        else:
            hits = anchors & set(_plain(text).split())
            if len(hits) < min(2, len(anchors)):
                continue
        if years:
            evidence_years = {int(value) for value in re.findall(r"\b(?:19|20)\d{2}\b", text)}
            acceptable = years
            if status_lookup:
                acceptable = years | {max(years) + 1, max(years) + 2}
            if not acceptable & evidence_years:
                continue
        if camping_lookup and not re.search(r"\b(?:camping|campsite|kamperen|kampeer\w*|accommodation\w*)\b", text, re.IGNORECASE):
            continue
        seen.add(url)
        kept.append(item)
        if len(kept) >= limit:
            break
    return kept


def select_gabber_citations(answer, results):
    """Publish only cited, prefiltered sources; reject missing/invalid web grounding."""
    answer = re.split(r"(?im)^\s*(?:Bronnen|Sources)\s*:", answer or "", maxsplit=1)[0].strip()
    if not results:
        return _CITATION.sub("", answer).strip(), []
    # Normalize model-added hyperlinks; the server owns the final source list.
    answer = re.sub(r"\[(\d+)\]\(https?://[^\s)]+\)", r"[\1]", answer)
    used = []
    for match in _CITATION.finditer(answer):
        for raw in match.group(1).split(","):
            index = int(raw.strip())
            if not 1 <= index <= len(results):
                return UNCONFIRMED_WEB_REPLY, []
            if index not in used:
                used.append(index)
    if not used:
        return UNCONFIRMED_WEB_REPLY, []
    # Do not let an uncited, model-invented URL masquerade as a source.
    allowed_urls = {item["url"] for item in results}
    if any(url.rstrip(".,;!") not in allowed_urls for url in re.findall(r"https?://[^\s)]+", answer)):
        return UNCONFIRMED_WEB_REPLY, []
    mapping = {old: new for new, old in enumerate(used, start=1)}
    answer = _CITATION.sub(
        lambda match: "[" + ", ".join(str(mapping[int(value.strip())]) for value in match.group(1).split(",")) + "]",
        answer,
    )
    return answer, [results[index - 1] for index in used]


_EVENT_WORD = re.compile(
    r"\b(?:feest(?:en|je|jes|juhs)?|fesstjuhs|party(?:'s|s)?|raves?|festival(?:s)?|evenement(?:en)?|optreden(?:s)?|uitgaan)\b",
    re.IGNORECASE,
)
_EVENT_PERIOD = re.compile(
    r"\b(?:dit|komend|aankomend|volgend)\s+weekend\b|"
    r"\b(?:vandaag|morgen|vanavond|deze\s+(?:vrijdag|zaterdag|zondag))\b",
    re.IGNORECASE,
)
_EVENT_DETAIL = re.compile(
    r"\b(?:line[\s-]?up|wie\s+(?:draait|speelt|staat)|welke\s+(?:dj|artiest)|"
    r"artiesten|namen|tickets?|kaartjes?|locatie|adres|hoe\s+laat|timetable|set[- ]tijden)\b",
    re.IGNORECASE,
)
_LOCATION_PATTERNS = (
    re.compile(r"\b(?:ik|we|wij)\s+(?:woon|wonen|woonachtig)\s+in\s+([a-zà-ÿ][a-zà-ÿ'’\-]*(?:\s+[a-zà-ÿ][a-zà-ÿ'’\-]*){0,3})", re.IGNORECASE),
    re.compile(r"\b(?:in de buurt van|omgeving van|regio)\s+([a-zà-ÿ][a-zà-ÿ'’\-]*(?:\s+[a-zà-ÿ][a-zà-ÿ'’\-]*){0,3})", re.IGNORECASE),
    re.compile(r"\bin\s+((?!(?:de|het|een|dit|deze|mijn|jouw)\b)[a-zà-ÿ][a-zà-ÿ'’\-]*(?:\s+[a-zà-ÿ][a-zà-ÿ'’\-]*){0,3})", re.IGNORECASE),
)
_LOCATION_STOP = {"dit", "deze", "komend", "aankomend", "volgend", "weekend", "vandaag", "morgen", "vanavond", "en", "maar", "want", "daar", "dus", "we", "wij", "ik", "is", "zijn", "er", "ook", "iets", "het", "de", "een", "hier", "in"}


def _is_upcoming_event_question(text: str) -> bool:
    return bool(_EVENT_WORD.search(text or "") and _EVENT_PERIOD.search(text or ""))


def _extract_location(text: str) -> str | None:
    q = " ".join((text or "").split())
    for pattern in _LOCATION_PATTERNS:
        match = pattern.search(q)
        if not match:
            continue
        words = []
        for word in match.group(1).strip(" ,.!?;:").split():
            cleaned = word.strip(" ,.!?;:")
            if cleaned.lower() in _LOCATION_STOP:
                break
            words.append(cleaned)
            if len(words) == 4:
                break
        if words:
            return " ".join(words).title()
    return None


def _weekend_dates(text: str, today=None) -> str:
    from datetime import date, datetime, timedelta
    from zoneinfo import ZoneInfo

    current = today or datetime.now(ZoneInfo("Europe/Amsterdam")).date()
    if not isinstance(current, date):
        current = date.today()
    saturday = current + timedelta(days=(5 - current.weekday()) % 7)
    if current.weekday() == 6:
        saturday = current - timedelta(days=1)
    if "volgend weekend" in (text or "").lower():
        saturday += timedelta(days=7)
    sunday = saturday + timedelta(days=1)
    return f"{saturday:%d-%m-%Y} en {sunday:%d-%m-%Y}"



_EVENT_MONTH_NAMES = {
    1: ("january", "jan", "januari"),
    2: ("february", "feb", "februari"),
    3: ("march", "mar", "maart"),
    4: ("april", "apr"),
    5: ("may", "mei"),
    6: ("june", "jun", "juni"),
    7: ("july", "jul", "juli"),
    8: ("august", "aug", "augustus"),
    9: ("september", "sep"),
    10: ("october", "oct", "oktober", "okt"),
    11: ("november", "nov"),
    12: ("december", "dec"),
}


def _event_date_in_text(text: str, day: int, month: int, year: int) -> bool:
    import unicodedata

    value = unicodedata.normalize("NFKD", text or "").lower()
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    day_token = rf"0?{day}"
    month_token = rf"0?{month}"
    year_token = re.escape(str(year))
    numeric_patterns = (
        rf"\b{day_token}[-/.]{month_token}[-/.]{year_token}\b",
        rf"\b{year_token}[-/.]{month_token}[-/.]{day_token}\b",
    )
    month_names = "|".join(re.escape(name) for name in _EVENT_MONTH_NAMES.get(month, ()))
    word_patterns = (
        rf"\b{day_token}\s+(?:{month_names})\s+{year_token}\b",
        rf"\b(?:{month_names})\s+{day_token}(?:st|nd|rd|th)?[,]?\s+{year_token}\b",
    )
    return any(re.search(pattern, value, re.IGNORECASE) for pattern in numeric_patterns + word_patterns)


def filter_gabber_event_results(results: list[dict], query: str) -> list[dict]:
    """Keep only event results that support the requested date and, if local, place."""
    dates = [
        (int(day), int(month), int(year))
        for day, month, year in re.findall(r"\b(\d{2})-(\d{2})-(\d{4})\b", query or "")
    ]
    month_lookup = {
        name: month
        for month, names in _EVENT_MONTH_NAMES.items()
        for name in names
    }
    month_pattern = "|".join(
        re.escape(name)
        for names in _EVENT_MONTH_NAMES.values()
        for name in names
    )
    for day, month_name, year in re.findall(
        rf"\b(\d{{1,2}})\s+({month_pattern})\s+(\d{{4}})\b",
        query or "",
        re.IGNORECASE,
    ):
        date_tuple = (int(day), month_lookup[month_name.lower()], int(year))
        if date_tuple not in dates:
            dates.append(date_tuple)
    if not dates:
        return results or []

    place_match = re.search(
        rf"\bhardcore\s+party\s+(.+?)\s+\d{{1,2}}\s+(?:{month_pattern})\s+\d{{4}}\b",
        query or "",
        re.IGNORECASE,
    )
    place = place_match.group(1).strip(" ,.!?") if place_match else ""
    if place.lower() == "nederland":
        place = ""

    event_signal = re.compile(
        r"\b(?:line[\s–-]?up|festival|gabber|hardcore|party|feest|event|evenement|optreden|agenda)\b",
        re.IGNORECASE,
    )
    kept = []
    for item in results or []:
        text = " ".join((
            str(item.get("title") or ""),
            str(item.get("snippet") or ""),
            str(item.get("url") or ""),
        ))
        if place and not re.search(r"(?<!\w)" + re.escape(place) + r"(?!\w)", text, re.IGNORECASE):
            continue
        # When a city and exact date are requested, those two checks already
        # anchor the result to the event. Listings sometimes omit genre/event
        # words from their title and snippet, so require the signal only for
        # nationwide searches where there is no specific place to match.
        if not place and not event_signal.search(text):
            continue
        if not any(_event_date_in_text(text, int(day), int(month), int(year)) for day, month, year in dates):
            continue
        kept.append(item)
    return kept



def _confirmed_lineup_query_names(limit: int = 3) -> list[str]:
    """Load a few current, publicly confirmed MHJH names for targeted lookups."""
    from pathlib import Path
    import json

    knowledge_path = Path(__file__).resolve().parent / "gabber_yello" / "knowledge" / "lineup.json"
    try:
        with knowledge_path.open("r", encoding="utf-8") as handle:
            artists = json.load(handle).get("confirmed_artists", [])
    except (OSError, ValueError, TypeError):
        return []
    return [
        str(item.get("name")).strip()
        for item in artists
        if isinstance(item, dict) and str(item.get("name") or "").strip()
    ][:limit]


def build_gabber_web_query(message: str, history: list[dict] | None = None, today=None, resolved=None) -> tuple[str, bool]:
    """Build a Dutch, local, date-anchored query for current party searches.

    A location correction can follow an event question, so use recent user turns
    only; earlier assistant answers are never copied into the search query.
    """
    context = resolved or resolve_gabber_context(message, history, today)
    user_turns = [
        item.get("content", "")
        for item in (history or [])[-12:]
        if item.get("role") == "user" and isinstance(item.get("content"), str)
    ]
    event_turns = [text for text in user_turns + [message or ""] if _is_upcoming_event_question(text)]
    current_location = _extract_location(message)
    is_event_detail = bool(event_turns and _EVENT_DETAIL.search(message or ""))
    followup_event = bool(event_turns and current_location and not _is_upcoming_event_question(message))
    named_period = bool(context.subjects and not context.needs_clarification and _EVENT_PERIOD.search(message or ""))
    if not _is_upcoming_event_question(message) and not followup_event and not is_event_detail and not named_period:
        return ("" if context.needs_clarification else context.query), False

    event_text = (message or "") if _is_upcoming_event_question(message) or named_period else event_turns[-1]
    location = current_location
    if not location:
        for prior in reversed(user_turns):
            location = _extract_location(prior)
            if location:
                break
    location = location or "Nederland"
    region_suffix = "" if location.lower() == "nederland" else ", Nederland"
    period = _EVENT_PERIOD.search(event_text)
    period_label = period.group(0).lower() if period else "dit weekend"
    dates = _weekend_dates(event_text, today) if "weekend" in period_label else ""
    first_date = re.search(r"\b(\d{2})-(\d{2})-(\d{4})\b", dates)
    if first_date:
        day, month, year = (int(value) for value in first_date.groups())
        month_name = _EVENT_MONTH_NAMES[month][0]
        date_part = f"{day} {month_name} {year}"
    else:
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        current_day = today or datetime.now(ZoneInfo("Europe/Amsterdam")).date()
        target_day = current_day + timedelta(days=1 if period_label == "morgen" else 0)
        weekday_names = {"deze vrijdag": 4, "deze zaterdag": 5, "deze zondag": 6}
        if period_label in weekday_names:
            target_day = current_day + timedelta(days=(weekday_names[period_label] - current_day.weekday()) % 7)
        date_part = f"{target_day.day} {_EVENT_MONTH_NAMES[target_day.month][0]} {target_day.year}"
    named = context.subjects[0] if len(context.subjects) == 1 and not context.needs_clarification else None
    query = f"{named} festival {date_part}" if named else f"hardcore party {location} {date_part}"
    if is_event_detail:
        query += " line-up"
        if not named:
            for artist in _confirmed_lineup_query_names()[:2]:
                query += f" {artist}"
    return query[:300], True



def find_mhjh_lineup_overlap(results: list[dict]) -> list[str]:
    """Return confirmed MHJH artists found in external event search results."""
    from pathlib import Path
    import json

    knowledge_path = Path(__file__).resolve().parent / "gabber_yello" / "knowledge" / "lineup.json"
    try:
        with knowledge_path.open("r", encoding="utf-8") as handle:
            artists = json.load(handle).get("confirmed_artists", [])
    except (OSError, ValueError, TypeError):
        return []

    event_results = []
    event_signal = re.compile(
        r"\b(?:line[\s-]?up|festival|gabber party|hardcore party|event|evenement|feest|optreden|agenda)\b",
        re.IGNORECASE,
    )
    for item in results or []:
        url = str(item.get("url") or "").lower()
        if "komttiedanhe.nl" in url or "mhjhevents.nl" in url:
            continue
        result_text = " ".join((
            str(item.get("title") or ""),
            str(item.get("snippet") or ""),
        ))
        if event_signal.search(result_text):
            event_results.append(result_text.lower())

    matches = []
    for artist in artists:
        name = str(artist.get("name") or "").strip()
        aliases = [name, *artist.get("aliases", [])]
        if name and any(
            re.search(r"(?<!\w)" + re.escape(str(alias).strip().lower()) + r"(?!\w)", result_text)
            for alias in aliases if str(alias).strip()
            for result_text in event_results
        ):
            matches.append(name)
    return matches



def get_official_mhjh_ticket_url() -> str | None:
    """Read the canonical ticket shop URL from reviewed MHJH knowledge."""
    from pathlib import Path
    import json

    knowledge_path = Path(__file__).resolve().parent / "gabber_yello" / "knowledge" / "tickets.json"
    try:
        with knowledge_path.open("r", encoding="utf-8") as handle:
            value = json.load(handle).get("official_ticket_url")
    except (OSError, ValueError, TypeError):
        return None
    return value if isinstance(value, str) and value.startswith("https://") else None

