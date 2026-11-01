"""Selective MHJH and Hardcore knowledge loader for Gabber Yello.

Small operational JSON blocks and reviewed Hardcore Markdown sections are
retrieved locally. Only relevant excerpts enter the model prompt, keeping both
answers and token use under control.
"""

from functools import lru_cache
import json
from pathlib import Path
import re
import unicodedata

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "gabber_yello" / "knowledge"
HARDCORE_DIR = KNOWLEDGE_DIR / "hardcore"
KNOWLEDGE_FILES = (
    "mhjh.json",
    "gabber_yello.json",
    "event.json",
    "mijnmhjh.json",
    "lootjesjacht.json",
    "arcade.json",
    "lineup.json",
    "tickets.json",
    "whitehouse.json",
    "partyinfo.json",
    "merch.json",
    "resale.json",
    "partybus.json",
)

STOPWORDS = {
    "de", "het", "een", "en", "of", "van", "voor", "met", "naar", "is",
    "zijn", "wat", "wie", "waar", "hoe", "welke", "dat", "dit", "die",
    "ik", "jij", "je", "mij", "mijn", "er", "om", "op", "in", "te",
}

QUERY_ALIASES = (
    (("den haag hakkuh", "de haag hakke", "haag hakke"), " ech heftag gizmo hans glock darkraver 1993 2023 "),
    (("ech heftig", "echt heftig", "ech heftag"), " ech heftag de haag hakke gizmo maarten visser "),
    (("komt tie dan he", "kom tie dan he", "komtie dan he"), " dj norman darkraver kom tie dan he 2005 "),
    (("eerste echte dj", "eerste dj", "wie leerde draaien"), " pionier dj gizmo invloed geschiedenis "),
)

NAME_IGNORE = {
    "als", "ben", "dat", "deze", "dit", "een", "haha", "heb", "heyyy", "het", "hoe", "ik",
    "mijn", "maar", "nee", "vertel", "waar", "wanneer", "wat", "weet", "welke",
    "wie", "wil", "ja", "jij", "oei", "pfoe", "ken", "kennen",
}


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", (text or "").lower())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _terms(text: str) -> set[str]:
    return {word for word in _normalize(text).split() if len(word) >= 3 and word not in STOPWORDS}


def _expand_query(text: str) -> str:
    normalized = _normalize(text)
    additions = []
    for variants, expansion in QUERY_ALIASES:
        if any(_normalize(variant) in normalized for variant in variants):
            additions.append(expansion)
    return f"{text} {' '.join(additions)}".strip()


def _has_mhjh_name(text: str) -> bool:
    q = _normalize(text)
    return bool(re.search(r"\bkomt?\s*tie\s*dan\s*he\b|\bden haag hakkuh\b|\bde haag hakke\b|\bech heft(?:ig|ag)\b", q))


def _mhjh_naming_note() -> str:
    return (
        "MHJH-NAMEN — ORGANISATOR, FEEST EN PLATEN UIT ELKAAR HOUDEN:\n"
        "- MHJH betekent Mijn Huis Jouw Huis. MHJH Events is de organisator. Het door MHJH georganiseerde feest/concept heet "
        "Komt Tie Dan He – Den Haag Hakkûh; Den Haag Hakkûh II is de tweede editie. "
        "Komt Tie Dan He is dus een feestnaam van MHJH, niet de naam van de organisatie.\n"
        "- De afzonderlijke track Kom Tie Dan Hè! uit 2005 is van DJ Norman vs. Darkraver. "
        "Top 40: hoogste positie 4, acht weken totaal in de lijst. Leid daar geen aantal weken op positie 4 uit af.\n"
        "- De Haag Hakke!! van Éch Heftag! uit 1993 (DJ Gizmo en Maarten Visser) en "
        "Den Haag Hakkûh van Hans Glock, The Darkraver en DJ Gizmo uit 2023 zijn afzonderlijke tracks.\n"
        "Bij een vraag over de MHJH-relatie: leg eerst concreet uit wie het feest organiseert en hoe het heet. "
        "Bij 'ik dacht Den Haag Hakkûh': bevestig dat die naam inderdaad bij dat MHJH-feest hoort; "
        "maak van de twee delen van de feesttitel geen twee losse concurrerende evenementen. "
        "Voeg de verwijzing naar bestaande platen alleen toe wanneer dat de vraag helpt. "
        "Bij 'ik snap het niet' geef maximaal drie korte zinnen: MHJH Events organiseert het feest, "
        "dat heet Komt Tie Dan He – Den Haag Hakkûh, en de gelijknamige track is een afzonderlijk muzieknummer. "
        "Herhaal geen verhaal over vibes en laat een slotzin als Hopelijk is het nu duidelijk achterwege. "
        "Artiestcredits bewijzen geen eigendom of afwezigheid van rechten: verzin geen MHJH-rechten, licenties, "
        "toestemming, contracten of labelrol en concludeer ook niet dat MHJH geen rechten heeft. "
        "Zeg evenmin in het algemeen dat MHJH nooit tracks of anthems uitbrengt."
    )


_NAMING_FOLLOWUP = re.compile(
    r"(?:(?:die|dat|dit) snap ik niet(?: kun je dat beter uitleggen)?|"
    r"kun je (?:dat|dit) (?:(?:beter|simpeler|nog eens) )?uitleggen|"
    r"wat bedoel je(?: daarmee)?|hoe bedoel je(?: dat)?)"
)


def _mhjh_naming_context(message: str, history=None) -> str | None:
    q = _normalize(message)
    if _has_mhjh_name(message) or (
        "mhjh" in q.split() and re.search(r"\b(?:track|nummer|plaat|naam|titel|feest|organisator)\b", q)
    ):
        return _mhjh_naming_note()
    if not _NAMING_FOLLOWUP.fullmatch(q):
        return None
    # User turns supply only a bounded topic anchor, never factual claims.
    for turn in reversed((history or [])[-8:]):
        if turn.get("role") != "user" or not isinstance(turn.get("content"), str):
            continue
        previous = _normalize(turn["content"])
        if _NAMING_FOLLOWUP.fullmatch(previous):
            continue
        return _mhjh_naming_note() if _has_mhjh_name(previous) else None
    return None


def _disambiguation_note(text: str) -> str | None:
    q = _normalize(text)
    if ("favoriet" in q and any(term in q for term in ("jouw", "jou", "jij", "je"))) or (
        re.search(r"\bbeste (?:hardcore )?(?:track|nummer|plaat|artiest)\b", q)
        and any(term in q.split() for term in ("jouw", "jou", "jij", "je"))
    ):
        return (
            "PERSONA-SMAAK — KIEZEN OP EEN CRITERIUM, GEEN VERZONNEN FAVORIET:\n"
            "Er is geen vastgelegde absolute favoriete track of ranglijst. Early is het vertrekpunt, maar sluit aan bij elke stijl. "
            "Je mag op een concreet muzikaal criterium een track of artiest kiezen die in de overige aangeleverde kennis "
            "daadwerkelijk met die credits staat. Als de geselecteerde kennis geen concreet artiest-titelpaar bevat, "
            "noem dan GEEN concrete track of artiest als voorbeeld; bespreek alleen je muzikale criterium. "
            "Bedenk geen titel uit algemene modelkennis om het antwoord toch af te maken. "
            "Presenteer de keuze als smaak voor deze vraag, niet als eigen koop-, feest- of jeugdherinnering en niet als officiële MHJH-ranglijst. "
            "Sluit niet automatisch af met een tegenvraag."
        )
    if any(term in q for term in ("anekdote", "anekdotes", "sterk verhaal", "sterke verhalen")):
        return (
            "HARD GESPREKSVANGRAIL — GEEN ANEKDOTE VERZINNEN:\n"
            "Er staat voor deze vraag geen concreet, gecontroleerd persoonlijk anekdoteverhaal in de geselecteerde kennis. "
            "Noem daarom geen zogenaamd echt optreden, lange set, gabberklompen, rave runners, backstage-incident, "
            "verlaten fabriek of citaat. Zeg kort en natuurlijk dat je de historische hoofdlijnen kent, maar geen specifieke "
            "anekdote betrouwbaar kunt navertellen. Je mag toevoegen dat verhalen van mensen die erbij waren waardevol zijn, "
            "maar sluit niet af met een automatische tegenvraag."
        )
    if any(term in q for term in ("xtc", "ecstasy", "pillen", "pilletje")):
        return (
            "HARD GESPREKSVANGRAIL — MIDDELEN NIET ROMANTISEREN:\n"
            "Reageer warm en niet-prekerig, maar bevestig niet dat xtc of pillen vroeger echter, beter, veiliger of onbezorgder waren. "
            "Verheerlijk geheugenverlies of risico niet, geef geen gebruiksinstructie en verzin geen ervaring. Sluit aan bij de "
            "festivalherinnering en muziek. Alleen bij concreet gevaar geef je een korte serieuze veiligheidsreactie."
        )
    if _has_mhjh_name(text):
        return _mhjh_naming_note()
    return None


# Explicit person references work independently of capitalization.
_PERSON_CUE = re.compile(
    r"(?P<birthday>\bverjaardag(?:\s+gehad)?\s+van\b)|"
    r"(?P<identity>\b(?:ken(?:nen)?\s+(?:je|jij|jullie)|wie\s+is)\b)",
    re.IGNORECASE,
)
_PERSON_TAIL_STOP = {
    "was", "waren", "is", "zijn", "heeft", "had", "heb", "hebben", "he",
    "nou", "echt", "ook", "wel", "niet", "al", "eigenlijk", "dan", "toch",
    "en", "maar", "omdat", "want", "die", "dat", "het", "op", "in",
    "gezellig", "leuk", "druk", "gisteren", "vrijdag",
}


def _explicit_person_reference(text: str):
    match = _PERSON_CUE.search(text or "")
    if not match:
        return None
    tail = (text or "")[match.end():].lstrip(" @")
    name_match = re.match(
        r"[A-Za-zÀ-ÿ][\wÀ-ÿ'’\-]*(?:[ \t]+[A-Za-zÀ-ÿ][\wÀ-ÿ'’\-]*){0,3}",
        tail,
    )
    if not name_match:
        return None
    words = []
    for word in name_match.group(0).split():
        if _normalize(word) in _PERSON_TAIL_STOP:
            break
        words.append(word)
    if not words:
        return None
    name = " ".join(words)
    if _normalize(words[0]) in (STOPWORDS | NAME_IGNORE | {"iemand", "iets", "ons", "jullie", "mensen"}):
        return None
    return ("birthday" if match.group("birthday") else "identity", name)


@lru_cache(maxsize=1)
def _reviewed_name_corpus() -> str:
    # Local reviewed files are evidence; assistant messages never join this corpus.
    parts = [block.get("answer", "") for block in _load_mhjh_knowledge()]
    parts += [section["title"] + "\n" + section["body"] for section in _load_hardcore_sections()]
    return " " + _normalize("\n".join(parts)) + " "


def _name_is_reviewed(name: str) -> bool:
    return " " + _normalize(name) + " " in _reviewed_name_corpus()


def _prior_unsupported_reputation(name: str, history) -> bool:
    needle = " " + _normalize(name) + " "
    for turn in (history or [])[-8:]:
        if turn.get("role") != "assistant" or not isinstance(turn.get("content"), str):
            continue
        for clause in re.split(r"[.!?;]|\bmaar\b", turn["content"], flags=re.IGNORECASE):
            q = _normalize(clause)
            if needle not in " " + q + " ":
                continue
            if any(denial in q for denial in ("niet betrouwbaar", "niet specifiek", "niet plaatsen", "niet onderbouwd")):
                continue
            if re.search(r"\b(?:bekend\w*|goede naam|grote naam|legende|icoon|pionier|dj|artiest)\b", q):
                return True
    return False


def unverified_person_reply(message: str, history=None) -> str | None:
    """Bounded smalltalk/identity fallback; it does not identify unknown people."""
    # Keep real help requests and distress on the normal assistance route.
    if re.search(
        r"\b(?:help|pijn|ziek|onwel|ehbo|paniek|politie|letsel|bedreigd|bewusteloos|oververhit|zelfmoord)\b",
        _normalize(message),
    ):
        return None
    reference = _explicit_person_reference(message)
    if not reference:
        return None
    kind, name = reference
    if _normalize(name) in {"hem", "haar", "die", "diegene"}:
        reference = None
        for turn in reversed((history or [])[-8:]):
            if turn.get("role") != "user" or not isinstance(turn.get("content"), str):
                continue
            reference = _explicit_person_reference(turn["content"])
            # The nearest substantive user topic decides; don't use assistant claims.
            break
        if not reference or _normalize(reference[1]) in {"hem", "haar", "die", "diegene"}:
            return None
        name = reference[1]
        kind = "identity"
    if _name_is_reviewed(name):
        return None
    if kind == "birthday":
        q = _normalize(message)
        if "?" in message or re.search(r"\b(?:niet|ongezellig|vervelend|ruzie)\b", q) or not re.search(r"\b(?:ik|we|wij|gehad|geweest)\b", q):
            return None
        if re.search(r"\b(?:gezellig|leuk|tof|mooi)\b", q):
            return "Klinkt gezellig, maat! Mooi dat je een leuke avond hebt gehad."
        if "druk" in q.split():
            return "Dat was dus een drukke avond, maat."
        return "Je was dus op een verjaardag, maat."
    display = name[0].upper() + name[1:]
    if _prior_unsupported_reputation(name, history):
        return (
            "Dat ik die naam eerder als bekend in de scene neerzette, was niet onderbouwd. "
            f"Ik kan {display} niet betrouwbaar plaatsen."
        )
    return f"Ik kan {display} niet betrouwbaar plaatsen."



def attributed_knowledge_reply(question: str, answer: str, selected_context: str | None) -> str:
    """Keep an explicitly marked, source-bound card intact when its claim is used."""
    named_text = " " + _normalize((question or "") + " " + (answer or "")) + " "
    answer_text = " " + _normalize(answer or "") + " "
    # Cards come only from the selected reviewed knowledge, never chat history.
    for section in re.split(r"(?m)^### ", selected_context or ""):
        fields = {}
        for key in ("namen", "trefwoorden", "antwoord"):
            match = re.search(r"^Brongebonden " + key + r": ([^\n]{1,2000})$", section, re.MULTILINE)
            if match:
                fields[key] = match.group(1).strip()
        if len(fields) != 3:
            continue
        names = [_normalize(value) for value in fields["namen"].split("|") if value.strip()]
        terms = [_normalize(value) for value in fields["trefwoorden"].split("|") if value.strip()]
        if any(" " + name + " " in named_text for name in names) and any(
            " " + term + " " in answer_text for term in terms
        ):
            return fields["antwoord"]
    return answer


def _unknown_name_note(text: str, selected_context: str) -> str | None:
    """Flag capitalized names that are absent from the selected knowledge."""
    candidates = []
    for raw in re.findall(r"\b[A-ZÀ-Ý][A-Za-zÀ-ÿ0-9_-]{2,}\b", text or ""):
        name = _normalize(raw)
        if name and name not in NAME_IGNORE and name not in candidates:
            candidates.append(name)

    reference = _explicit_person_reference(text)
    if reference and not _name_is_reviewed(reference[1]):
        name = _normalize(reference[1])
        if name not in candidates:
            candidates.append(name)

    if not candidates:
        return None

    context_normalized = _normalize(selected_context)
    unknown = [name for name in candidates if f" {name} " not in f" {context_normalized} "]
    if not unknown:
        return None

    display = ", ".join(unknown)
    return (
        f"HARD NAAMVANGRAIL — ONBEKENDE NAAM/TERM: {display}. "
        "De genoemde naam komt niet voor in de geselecteerde gecontroleerde kennis. Leid geen identiteit af uit andere "
        "woorden in de vraag, zoals pensioen, feest, dj of optreden. Noem deze persoon niet bekend, Haags, Rotterdams, "
        "artiest, pionier of icoon en verzin geen loopbaan of datum. Zeg kort dat je de naam niet betrouwbaar kunt plaatsen "
        "en het moment niet weet. Eén gerichte vraag welke persoon wordt bedoeld is toegestaan."
    )


@lru_cache(maxsize=1)
def _load_mhjh_knowledge():
    blocks = []
    for filename in KNOWLEDGE_FILES:
        path = KNOWLEDGE_DIR / filename
        with path.open("r", encoding="utf-8") as handle:
            block = json.load(handle)
            block["_file"] = filename
            blocks.append(block)
    return tuple(blocks)


@lru_cache(maxsize=1)
def _load_hardcore_sections():
    sections = []
    if not HARDCORE_DIR.exists():
        return tuple()

    for path in sorted(HARDCORE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        current_title = path.stem
        current_lines = []

        def store_section():
            body = "\n".join(current_lines).strip()
            if body:
                searchable = f"{current_title}\n{body}"
                sections.append({
                    "title": current_title,
                    "body": body,
                    "normalized": _normalize(searchable),
                    "terms": _terms(searchable),
                    "file": path.name,
                })

        for line in text.splitlines():
            if line.startswith("## ") or line.startswith("### "):
                store_section()
                current_title = re.sub(r"^#{2,3}\s+(?:\d+\.\s*)?", "", line).strip()
                current_lines = []
            elif line.startswith("# "):
                continue
            else:
                current_lines.append(line)
        store_section()

    return tuple(sections)


def _hardcore_matches(message: str, limit: int = 3) -> list[str]:
    expanded = _expand_query(message)
    normalized = _normalize(expanded)
    query_terms = _terms(expanded)
    if not normalized or not query_terms:
        return []

    scored = []
    for order, section in enumerate(_load_hardcore_sections()):
        title_normalized = _normalize(section["title"])
        title_terms = _terms(section["title"])
        overlap = query_terms & section["terms"]
        if not overlap:
            continue

        score = len(overlap) * 3
        score += len(query_terms & title_terms) * 8
        if title_normalized and title_normalized in normalized:
            score += 20
        if normalized in section["normalized"]:
            score += 6
        scored.append((score, -order, section))

    scored.sort(reverse=True, key=lambda item: (item[0], item[1]))
    excerpts = []
    used_chars = 0
    for score, _, section in scored[:limit]:
        if score < 3:
            continue
        excerpt = f"### {section['title']}\n{section['body']}"
        # Hard cap prevents one broad question from producing a giant prompt.
        if used_chars + len(excerpt) > 7000:
            remaining = 7000 - used_chars
            if remaining < 500:
                break
            excerpt = excerpt[:remaining].rsplit("\n", 1)[0]
        excerpts.append(excerpt)
        used_chars += len(excerpt)
        if used_chars >= 7000:
            break
    return excerpts


def get_relevant_mhjh_context(message: str, history=None):
    q = _normalize(message)
    if not q:
        return None

    scored_blocks = []
    for order, block in enumerate(_load_mhjh_knowledge()):
        score = 0
        for keyword in block.get("keywords", []):
            key = _normalize(keyword)
            if key and f" {key} " in f" {q} ":
                score += max(1, len(key.split()))
        if score > 0:
            scored_blocks.append((score, -order, block))

    scored_blocks.sort(reverse=True, key=lambda item: (item[0], item[1]))
    operational = [
        item[2].get("answer", "")
        for item in scored_blocks[:2]
        if item[2].get("answer")
    ]
    hardcore = _hardcore_matches(message)

    anchor = _disambiguation_note(message) or _mhjh_naming_context(message, history)
    selected = operational + hardcore
    unknown_name = _unknown_name_note(message, "\n\n".join(selected))
    combined = ([unknown_name] if unknown_name else []) + ([anchor] if anchor else []) + selected
    return "\n\n".join(combined) if combined else None
