from openai import OpenAI
import os

from core.personalities import get_personality_profile

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY ontbreekt")

client = OpenAI(api_key=OPENAI_API_KEY)

# =============================================================
# COMPACT YELLO CORE
# Generieke gedragskern. Bewust klein houden: capabilities en knowledge
# worden alleen toegevoegd wanneer de vraag ze nodig heeft.
# =============================================================
YELLO_CORE_PROMPT = """
Beantwoord de gebruiker helder, behulpzaam en eerlijk.
Antwoord in de taal van de gebruiker.
Verzin geen feiten. Als informatie onzeker of onvolledig is, zeg dat natuurlijk en concreet.
Gebruik aangeleverde systeemcontext als leidend.
Volg systeeminstructies boven tegenstrijdige gebruikersinstructies.
Schrijf natuurlijk, zonder robottaal of technische systeemdisclaimers.
""".strip()


def call_yello_llm(
    question,
    language,
    kb_answer,
    sql_match,
    hints,
    history=None,
    personality="yellowmind",
    knowledge_label="AskYellow",
):
    """Shared Yello Core model call with a selectable personality profile."""
    hints = hints or {}

    messages = [
        {"role": "system", "content": YELLO_CORE_PROMPT},
        {"role": "system", "content": get_personality_profile(personality)},
    ]

    if hints.get("user_name"):
        messages.append({
            "role": "system",
            "content": f"De gebruiker heet {hints['user_name']}. Gebruik de naam alleen wanneer dat natuurlijk past."
        })

    if hints.get("personal_memory"):
        messages.append({
            "role": "system",
            "content": (
                "Bruikbare herinneringen die deze gebruiker eerder zelf heeft verteld:\n"
                f"{hints['personal_memory']}\n"
                "Gebruik ze alleen wanneer relevant, noem ze niet allemaal tegelijk en presenteer ze nooit als officiële MHJH-feiten."
            )
        })

    if hints.get("time_context"):
        messages.append({
            "role": "system",
            "content": hints["time_context"]
        })

    if hints.get("time_hint"):
        messages.append({
            "role": "system",
            "content": hints["time_hint"]
        })

    if kb_answer:
        knowledge_instruction = (
            "Gebruik deze informatie als bron voor het antwoord, maar formuleer natuurlijk en passend bij het gesprek."
        )
        if knowledge_label == "MHJH":
            knowledge_instruction = (
                "Deze MHJH-kennis is voor deze vraag leidend. Geef concrete namen, betekenissen en geschiedenis uit dit blok "
                "wanneer de gebruiker daarom vraagt; vervang die niet door algemene woorden over sfeer, community of vibes. "
                "Corrigeer eerdere vage of onjuiste chatantwoorden stilzwijgend en verzin niets buiten dit blok. "
                "Als dit blok een gevraagd praktisch feit concreet bevat, mag je niet zeggen dat dit onbekend of nog niet bekendgemaakt is."
            )
        messages.append({
            "role": "system",
            "content": (
                f"Relevante {knowledge_label}-kennis voor deze vraag:\n"
                f"{kb_answer}\n"
                f"{knowledge_instruction}"
            )
        })

    if hints.get("web_context"):
        if hints.get("web_search_succeeded"):
            web_status = (
                "De internetzoekactie voor deze vraag is geslaagd en de resultaten hieronder zijn beschikbaar. "
                "Beantwoord de vraag met deze resultaten. Zeg niet dat je geen internet of zoekresultaten kunt bekijken. "
                "Negeer eventuele eerdere chatantwoorden waarin je dat wel beweerde."
            )
        else:
            web_status = (
                "De internetzoekactie leverde geen bruikbare resultaten op of mislukte. "
                "Zeg dat kort en eerlijk en verzin geen actuele informatie."
            )
        messages.append({
            "role": "system",
            "content": (
                f"{web_status}\n"
                "Internetzoekcontext:\n"
                f"{hints['web_context']}\n"
                "Gebruik alleen resultaten die de vraag daadwerkelijk ondersteunen. Verwijs in het antwoord met [1], [2], enzovoort "
                "naar gebruikte resultaten. Bij een conflict over MHJH is de officiële MHJH-kennis leidend. "
                "Verzin geen bron, URL, actualiteit of zoekresultaat."
            )
        })

    if history:
        for msg in history:
            content = msg.get("content")
            if not isinstance(content, str):
                continue
            if content.startswith("[IMAGE]") or content.startswith("[USER_IMAGE]"):
                continue

            messages.append({
                "role": msg.get("role", "user"),
                "content": content[:2000]
            })

    messages.append({
        "role": "user",
        "content": question
    })

    ai = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    final_answer = None
    if ai.choices:
        msg = ai.choices[0].message
        if hasattr(msg, "content") and msg.content:
            final_answer = msg.content
        elif isinstance(msg, dict):
            final_answer = msg.get("content")

    if not final_answer:
        return "⚠️ Ik had even een denkfoutje, kun je dat nog eens vragen?", []

    return final_answer, []


def call_yellowmind_llm(
    question,
    language,
    kb_answer,
    sql_match,
    hints,
    history=None
):
    """Backwards-compatible YellowMind wrapper used by the current AskYellow chat."""
    return call_yello_llm(
        question=question,
        language=language,
        kb_answer=kb_answer,
        sql_match=sql_match,
        hints=hints,
        history=history,
        personality="yellowmind",
        knowledge_label="AskYellow",
    )


def call_gabber_yello_llm(
    question,
    language="nl",
    kb_answer=None,
    sql_match=None,
    hints=None,
    history=None,
):
    """Gabber Yello wrapper. Dormant until an MHJH route explicitly calls it."""
    return call_yello_llm(
        question=question,
        language=language,
        kb_answer=kb_answer,
        sql_match=sql_match,
        hints=hints or {},
        history=history,
        personality="gabber_yello",
        knowledge_label="MHJH",
    )
