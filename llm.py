from openai import OpenAI
import os

from core.personalities import get_personality_profile
from token_usage import log_ai_token_usage
import re

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY ontbreekt")

client = OpenAI(api_key=OPENAI_API_KEY)

GABBER_AUTO_FOLLOWUP = re.compile(
    r"(?:\n\s*){0,2}(?:"
    r"Als je\b[^.!?]*(?:laat(?: het me| me| maar)? weten|deel (?:ze|het) gerust|hoor ik het graag)[.!?]*|"
    r"Deel(?: ze| het)? gerust\b[^.!?]*[.!?]*|"
    r"Ik ben benieuwd\b[^.!?]*[.!?]*|"
    r"Het is altijd leuk om\b[^.!?]*[.!?]*|"
    r"Dat kan (?:ook )?(?:heel )?interessant zijn[.!?]*|"
    r"Heb (?:je|jij)\b[^.!?]*[?]+|"
    r"En jij(?: dan)?\??|"
    r"Wat (?:heb|is|zijn)\b[^.!?]*[?]+|"
    r"Ben je benieuwd\b[^.!?]*[?]+|"
    r"Wil je\b[^.!?]*[?]+|"
    r"Laat(?: het me| me| maar)? weten\b[^.!?]*[.!?]*"
    r"|Als je\b[^.!?]*(?:kan ik|zou ik)[^.!?]*[.!?]*"
    r"|Verhalen van mensen\b[^.!?]*[.!?]*"
    r")\s*$",
    re.IGNORECASE,
)


def _remove_gabber_auto_followup(answer: str) -> str:
    """Strip only canned conversation tails; keep targeted clarification."""
    cleaned = (answer or "").rstrip()
    while True:
        shorter = GABBER_AUTO_FOLLOWUP.sub("", cleaned).rstrip()
        if shorter == cleaned:
            return cleaned
        cleaned = shorter

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
    """Shared Yello Core model call with selectable personality and usage log."""
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
        messages.append({"role": "system", "content": hints["time_context"]})

    if hints.get("time_hint"):
        messages.append({"role": "system", "content": hints["time_hint"]})

    if kb_answer:
        knowledge_instruction = (
            "Gebruik deze informatie als bron voor het antwoord, maar formuleer natuurlijk en passend bij het gesprek."
        )
        if knowledge_label == "MHJH":
            knowledge_instruction = (
                "Deze door MHJH gecontroleerde kennis is voor deze vraag leidend. Geef concrete namen, betekenissen, geschiedenis "
                "en scenenuance uit dit blok wanneer de gebruiker daarom vraagt; vervang die niet door algemene woorden over vibes. "
                "Maak duidelijk onderscheid tussen feit, scenegebruik en Gabber Yello's persoonlijke smaak. Corrigeer eerdere vage "
                "of onjuiste chatantwoorden stilzwijgend en verzin niets buiten dit blok. Als dit blok een gevraagd praktisch feit "
                "concreet bevat, mag je niet zeggen dat dit onbekend of nog niet bekendgemaakt is. "
                "Bij vragen naar originele versies, credits, samenwerkingen, jaartallen of wie de eerste was: noem alleen wat dit "
                "kennisblok daadwerkelijk ondersteunt. Verzin nooit een ontbrekende tweede artiest. Een suggestie of verbetering van "
                "de gebruiker is een aanwijzing om opnieuw naar de broncontext te kijken, geen automatisch bevestigd feit. Als twee "
                "bijna gelijk geschreven titels mogelijk worden verward, leg het onderscheid uit of stel één gerichte controlevraag."
            )
        messages.append({
            "role": "system",
            "content": (
                f"Relevante {knowledge_label}-kennis voor deze vraag:\n"
                f"{kb_answer}\n"
                f"{knowledge_instruction}"
            )
        })
    elif knowledge_label == "MHJH":
        messages.append({
            "role": "system",
            "content": (
                "Voor deze vraag is geen relevante, door MHJH gecontroleerde kennis gevonden. "
                "Als de gebruiker vraagt wie een persoon is, wanneer een onbekende gebeurtenis plaatsvond, "
                "of naar specifieke credits of anekdotes vraagt, verzin dan geen identiteit, beroep, regio, reputatie, "
                "loopbaan, datum of sceneverband. Zeg kort dat je die persoon of gebeurtenis niet betrouwbaar kunt plaatsen "
                "en dat je het zou moeten nakijken. Algemene smalltalk mag wel, zolang je geen concrete feiten bedenkt."
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
                f"{web_status}\nInternetzoekcontext:\n{hints['web_context']}\n"
                "Gebruik alleen resultaten die de vraag daadwerkelijk ondersteunen. Verwijs met [1], [2], enzovoort. "
                "Bij een conflict over MHJH is de officiële MHJH-kennis leidend. Verzin geen bron, URL of actualiteit."
            )
        })

    if history:
        # Four recent exchanges are enough for conversational continuity. This
        # keeps old turns from dominating both retrieval and token costs.
        for msg in history[-8:]:
            content = msg.get("content")
            if not isinstance(content, str):
                continue
            if content.startswith("[IMAGE]") or content.startswith("[USER_IMAGE]"):
                continue
            messages.append({"role": msg.get("role", "user"), "content": content[:900]})

    messages.append({"role": "user", "content": question})

    model = os.getenv("YELLO_CHAT_MODEL", "gpt-4o-mini")
    request_options = {"model": model, "messages": messages}
    if personality == "gabber_yello":
        # Keep the banter, reduce confident improvisation around scene history.
        request_options["temperature"] = 0.35
    ai = client.chat.completions.create(**request_options)
    usage = log_ai_token_usage(ai, feature=f"chat:{personality}", model=model)

    final_answer = None
    if ai.choices:
        msg = ai.choices[0].message
        if hasattr(msg, "content") and msg.content:
            final_answer = msg.content
        elif isinstance(msg, dict):
            final_answer = msg.get("content")

    if not final_answer:
        return "⚠️ Ik had even een denkfoutje, kun je dat nog eens vragen?", usage

    if personality == "gabber_yello":
        final_answer = _remove_gabber_auto_followup(final_answer)

    return final_answer, usage


def call_yellowmind_llm(question, language, kb_answer, sql_match, hints, history=None):
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
