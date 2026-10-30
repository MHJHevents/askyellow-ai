"""Bounded subject resolution; history supplies a topic, never verified facts."""

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
import re
from zoneinfo import ZoneInfo

from core.mhjh_context import _load_hardcore_sections, _normalize


_GENERIC = {
    "hardcore", "gabber", "hardstyle", "early", "uptempo", "terror", "speedcore",
    "club", "locatie", "festival", "rave", "resident dj", "dj", "liveact", "mc",
    "organisator", "feestconcept", "feest of evenement", "belgie", "duitsland",
    "frankrijk", "italie", "verenigde staten", "verenigd koninkrijk", "mhjh",
    "bpm", "onthouden", "belangrijk", "veiligheid", "niet verwarren", "bronnen",
    "voorbeeldantwoord", "gedragsregel", "status", "doel", "aansluiting",
    "rotterdam", "amsterdam", "den haag", "utrecht", "scheveningen", "eersel",
    "enschede", "groningen", "zaandam", "arnhem", "eindhoven", "leidschendam",
    "haarlemmermeer", "vijfhuizen", "heerlen", "maastricht", "oberhausen", "antwerpen",
    "frenchcore", "oldschool", "early rave", "early hardcore", "happy hardcore",
    "millennium", "millennium hardcore", "mainstream", "mainstream hardcore",
    "industrial", "industrial hardcore", "crossbreed", "drum and bass", "breakcore",
    "uptempo hardcore", "terrorcore", "freestyle", "harddance", "raw", "rawstyle",
    "techno", "house", "acid", "acid house", "new beat",
}
_FOLLOWUP = re.compile(
    r"\b(?:is|was|bestaat|gebeurt|gaat|komt|kan|doet|draait|speelt|staat|heeft|hebben)"
    r"\s+(?:het|dat|die|hij|zij|ze|er)\b|"
    r"\bweet\s+(?:je|jij)\s+(?:dat\s+)?zeker\b|"
    r"\b(?:dit|vorig|volgend)\s+jaar\s+(?:ook|dan|nog)\b|"
    r"\b(?:dit|komend|aankomend|volgend)\s+weekend(?:\s+(?:ook|dan|nog))?[?!.]*$|"
    r"\b(?:en|dus)\s+(?:wanneer|waar|hoe laat|welke datum)\b|"
    r"\b(?:wanneer|waar)\s+dan\b|"
    r"^(?:en\s+)?(?:hoe zit het met\s+|de\s+)?"
    r"(?:camping|line[ -]?up|tickets?|kaartjes|locatie|datum|timetable)\b",
    re.IGNORECASE,
)
_NEW_SUBJECT = re.compile(
    r"^(?:en\s+)?(?:wie (?:is|was)|wat (?:is|was)|wat weet je (?:van|over)|"
    r"vertel (?:(?:me|mij) )?(?:over|iets over))"
    r"\s+(?!(?:hij|zij|ze|die|dat|het)(?:\W|$))\S+|"
    r"\bhoe is het weer\b", re.IGNORECASE,
)
_CURRENT_STATUS = re.compile(
    r"\b(?:nog steeds|is er nog|bestaat\b.{0,70}\bnog|gaat .{0,35}door|"
    r"dit jaar|volgend jaar|(?:dit|komend|aankomend|volgend) weekend|"
    r"actueel|actuele|huidig|huidige|tegenwoordig|nieuwste|recentste)\b", re.IGNORECASE,
)
_RELATIVE_YEARS = (("dit jaar", 0), ("vorig jaar", -1), ("volgend jaar", 1))


def is_current_gabber_question(text):
    return bool(_CURRENT_STATUS.search(text or ""))


def _today(today=None):
    return today or datetime.now(ZoneInfo("Europe/Amsterdam")).date()


def _subject_candidate(value):
    value = re.sub(r"[*`_#]", "", value).strip(" \t:;,.!?‘’“”\"'")
    value = re.sub(r"^\d+[.)]?\s+", "", value)
    normalized = _normalize(value)
    if not 3 <= len(normalized) <= 70 or len(normalized.split()) > 6:
        return None
    if normalized in _GENERIC or re.match(r"^(?:vraag|wat|wie|waar|wanneer|hoe|waarom|zijn mening|haar mening)\b", normalized):
        return None
    if normalized.isdigit() or re.match(r"^(?:(?:begin|midden|eind) )?jaren?\b", normalized):
        return None
    date_words = {
        "januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus",
        "september", "oktober", "november", "december", "bpm", "uur", "tot", "en",
    }
    if all(word.isdigit() or word in date_words for word in normalized.split()):
        return None
    return value


@lru_cache(maxsize=1)
def _subject_aliases():
    aliases = {}
    for section in _load_hardcore_sections():
        title = section["title"]
        candidates = [title, *re.findall(r"\*\*([^*\n]+)\*\*", section["body"])]
        candidates.extend(re.split(r"\s+[—–/]\s+", title))
        candidates.append(re.split(
            r"\s+(?:was|is|stond|wanneer|locaties|meerdaags|weekendfestival|herinneringen|en de|en het|en MHJH|in Antwerpen)\b",
            title, maxsplit=1, flags=re.IGNORECASE,
        )[0])
        for candidate in candidates:
            name = _subject_candidate(candidate)
            if not name:
                continue
            key = _normalize(name)
            aliases.setdefault(key, name)
            short = re.sub(r"^(?:dj|the)\s+", "", key)
            if short != key and len(short) >= 4 and short not in _GENERIC:
                aliases.setdefault(short, name)
    return tuple(sorted(aliases.items(), key=lambda pair: -len(pair[0])))


def subjects_in(text):
    # Source footers are not conversational subjects; URLs are not facts.
    text = re.split(r"\b(?:Bronnen|Sources)\s*:", text or "", maxsplit=1, flags=re.IGNORECASE)[0]
    normalized = " " + _normalize(text[:1800]) + " "
    found = []
    consumed = []
    for alias, name in _subject_aliases():
        pattern = " " + alias + " "
        start = normalized.find(pattern)
        if start < 0:
            continue
        span = (start, start + len(pattern))
        if any(span[0] >= left and span[1] <= right for left, right in consumed):
            continue
        consumed.append(span)
        # A full and short spelling can refer to the same reviewed name.
        if name not in [item[1] for item in found]:
            found.append((start, name))
    return tuple(name for _, name in sorted(found))


def _resolve_year(text, today):
    lowered = (text or "").lower()
    for phrase, offset in _RELATIVE_YEARS:
        if phrase in lowered:
            return today.year + offset
    years = re.findall(r"\b(?:19|20)\d{2}\b", text or "")
    return int(years[-1]) if years else None


@dataclass(frozen=True)
class GabberContext:
    query: str
    subjects: tuple[str, ...] = ()
    followup: bool = False
    needs_clarification: bool = False
    current: bool = False
    year: int | None = None

    @property
    def clarification(self):
        if len(self.subjects) == 2:
            return f"Bedoel je {self.subjects[0]} of {self.subjects[1]}, maat?"
        return "Waar doel je precies op, maat?"

    @property
    def instruction(self):
        if not self.subjects or self.needs_clarification:
            return None
        if not self.followup and not self.current and self.year is None:
            return None
        names = ", ".join(self.subjects)
        year = f" De gevraagde tijdlaag is {self.year}." if self.year else ""
        return (
            f"Gespreksonderwerp voor deze vraag: {names}.{year} "
            "Deze onderwerpkeuze is alleen gesprekscontext, geen feitenbron. "
            "Gebruik de opnieuw geselecteerde kennis en relevante webbronnen voor de feiten. "
            "Een eerdere assistentuitspraak of het woord jaarlijks bewijst geen editie in een bepaald jaar. "
            "Neem pauzes, afgelastingen en verschillen tussen edities expliciet mee wanneer de vraag daarover gaat. "
            "Als een nieuwe webcheck niets bevestigt, mag je concrete gedateerde feiten uit gecontroleerde kennis "
            "wel benoemen, maar presenteer die niet als nieuw online bevestigd."
        )


def resolve_gabber_context(message, history=None, today=None):
    """Use at most six recent exchanges; never copy their assertions to knowledge."""
    current_day = _today(today)
    message = " ".join((message or "").split())[:600]
    explicit = subjects_in(message)
    followup = not explicit and len(message.split()) <= 24 and bool(_FOLLOWUP.search(message))
    if followup and _NEW_SUBJECT.search(message):
        followup = False
    subjects = explicit
    turns = [
        item for item in (history or [])[-12:]
        if item.get("role") in {"user", "assistant"} and isinstance(item.get("content"), str)
    ]
    anchor_index = len(turns)
    blocked = False
    if followup:
        # Explicit user topics outrank names introduced by an assistant.
        for index in range(len(turns) - 1, -1, -1):
            item = turns[index]
            if item["role"] != "user":
                continue
            named = subjects_in(item["content"])
            if named:
                subjects = named
                anchor_index = index
                break
            if _NEW_SUBJECT.search(item["content"].strip()):
                blocked = True
                break
        if not subjects and not blocked:
            # An assistant may identify a reviewed topic, not establish its facts.
            last_reply = next((item["content"] for item in reversed(turns) if item["role"] == "assistant"), "")
            subjects = subjects_in(last_reply)
        if len(subjects) != 1:
            return GabberContext(message, subjects[:3], True, True)

    year = _resolve_year(message, current_day)
    if followup and year is None:
        for item in reversed(turns[anchor_index:]):
            if item["role"] == "user":
                year = _resolve_year(item["content"], current_day)
                if year is not None:
                    break
    current = is_current_gabber_question(message)
    if followup and re.search(r"\bzeker\b", message, re.IGNORECASE) and year is not None:
        current = year >= current_day.year
    resolved = message
    for phrase, offset in _RELATIVE_YEARS:
        resolved = re.sub(r"\b" + phrase + r"\b", str(current_day.year + offset), resolved, flags=re.IGNORECASE)
    if followup:
        resolved = subjects[0] + ": " + resolved
    if current and year is None:
        year = current_day.year
        resolved += f" actuele status {year}"
    elif followup and year is not None and str(year) not in resolved:
        resolved += f" {year}"
    if current and re.search(r"\bzeker\b", message, re.IGNORECASE):
        resolved += " actuele status"
    return GabberContext(resolved[:300], subjects, followup, False, current, year)


def reviewed_edition_pause_reply(context, knowledge):
    """Fail safely to an explicit dated KB sentence, never infer an edition status.

    This is deliberately narrow: an uncited web answer must not suppress an
    already reviewed statement that a named subject skipped the requested year.
    No chat assertion, search snippet or invented positive edition is accepted.
    """
    if not knowledge or context.needs_clarification or len(context.subjects) != 1 or context.year is None:
        return None
    subject = context.subjects[0]
    names = {_normalize(subject), re.sub(r"^(?:the|dj)\s+", "", _normalize(subject))}
    for section in re.split(r"(?m)^### ", knowledge):
        header, _, body = section.partition("\n")
        if not any(" " + name + " " in " " + _normalize(header) + " " for name in names):
            continue
        body = re.sub(r"\*\*|\[[Nn]\d+(?:,?\s*[Nn]?\d+)*\]", "", body)
        for match in re.finditer(r"[^.!?\n]*\bsloeg\s+" + str(context.year) + r"\s+over\b[^.!?\n]*[.!?]?", body, re.IGNORECASE):
            sentence = match.group(0).strip()
            if not any(" " + name + " " in " " + _normalize(sentence) + " " for name in names):
                continue
            sentence = re.sub(r"^(?:Belangrijke tijdnuance|Stand op [^:]+)\s*:\s*", "", sentence, flags=re.IGNORECASE)
            after = body[match.end():].lstrip()
            if after.startswith("Het is daarmee niet definitief gestopt."):
                sentence += " Het is daarmee niet definitief gestopt."
            return sentence
    return None
