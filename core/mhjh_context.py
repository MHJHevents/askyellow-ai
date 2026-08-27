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
    "wie", "wil", "ja", "jij", "oei", "pfoe",
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


def _disambiguation_note(text: str) -> str | None:
    q = _normalize(text)
    if "favoriet" in q and any(term in q for term in ("jouw", "jou", "jij")):
        return (
            "HARD PERSONA-ANKER — GEEN FAVORIETE TRACK VERZINNEN:\n"
            "Gabber Yello heeft bewust geen vastgelegde absolute favoriete track. Haar smaak ligt vooral bij early, Haagse "
            "scenehistorie en platen met een eigen identiteit. Noem daarom geen exacte track als haar favoriet en verzin ook "
            "geen zogenaamd passend trackvoorbeeld om toch aan de opdracht te voldoen. Zeg vriendelijk dat ze geen eerlijke "
            "absolute nummer-één heeft en laat het daarbij; sluit niet af met een tegenvraag."
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
    if any(term in q for term in ("den haag hakkuh", "de haag hakke", "ech heftig", "ech heftag")):
        return (
            "HARD ANKERFEIT — Haagse titels niet vermengen:\n"
            "- Éch Heftag! — De Haag Hakke!! is de afzonderlijke hardcore-release uit 1993, "
            "verbonden met DJ Gizmo en producer Maarten Visser.\n"
            "- Hans Glock, The Darkraver & DJ Gizmo — Den Haag Hakkûh is de afzonderlijke moderne release uit 2023.\n"
            "- Zeg daarom niet dat de moderne track simpelweg een origineel van Gizmo & Darkraver of Gizmo & MC Ruffian heeft. "
            "Leg uit dat de gebruiker waarschijnlijk de oude en moderne Haagse titels aan elkaar koppelt."
        )
    if any(term in q for term in ("komt tie dan he", "kom tie dan he", "komtie dan he")):
        return (
            "HARD ANKERFEIT — Kom Tie Dan Hè!: de release uit 2005 is van DJ Norman vs. Darkraver. "
            "Schrijf hem niet toe aan Gizmo en voeg geen andere maker toe. De naam Komt Tie Dan He van MHJH is een culturele verwijzing naar deze plaat."
        )
    return None


def _unknown_name_note(text: str, selected_context: str) -> str | None:
    """Flag capitalized names that are absent from the selected knowledge."""
    candidates = []
    for raw in re.findall(r"\b[A-ZÀ-Ý][A-Za-zÀ-ÿ0-9_-]{2,}\b", text or ""):
        name = _normalize(raw)
        if name and name not in NAME_IGNORE and name not in candidates:
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


def get_relevant_mhjh_context(message: str):
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

    anchor = _disambiguation_note(message)
    selected = operational + hardcore
    unknown_name = _unknown_name_note(message, "\n\n".join(selected))
    combined = ([unknown_name] if unknown_name else []) + ([anchor] if anchor else []) + selected
    return "\n\n".join(combined) if combined else None
