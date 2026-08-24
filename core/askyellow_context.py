import json
import os
from functools import lru_cache

from yellowmind.askyellow_knowledge.knowledge_engine import match_question

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "yellowmind", "askyellow_knowledge")

# Alleen warme AskYellow-kennis. Shopper/search blijft bewust buiten deze route.
ALLOWED_KNOWLEDGE_FILES = (
    "knowledge_general.json",
    "knowledge_privacy.json",
)


@lru_cache(maxsize=1)
def _load_entries():
    entries = []
    for filename in ALLOWED_KNOWLEDGE_FILES:
        path = os.path.join(KNOWLEDGE_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue

        file_entries = data.get("entries", [])
        if isinstance(file_entries, list):
            entries.extend(file_entries)

    return entries


def get_relevant_askyellow_context(question: str):
    """Return één relevante AskYellow-kennispassage, of None bij geen match."""
    if not question:
        return None
    return match_question(question, _load_entries())
