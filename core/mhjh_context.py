"""Selective MHJH knowledge loader for Gabber Yello.

Loads small local JSON knowledge blocks and returns at most one relevant block.
No OpenAI call is used for retrieval, so irrelevant MHJH knowledge never enters
prompt context.
"""

from functools import lru_cache
import json
from pathlib import Path
import re
import unicodedata

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "gabber_yello" / "knowledge"
KNOWLEDGE_FILES = (
    "mhjh.json",
    "event.json",
    "mijnmhjh.json",
    "lootjesjacht.json",
    "arcade.json",
    "lineup.json",
)


def _normalize(text: str) -> str:
    """Normalize spelling/punctuation before deterministic keyword matching."""
    value = unicodedata.normalize("NFKD", (text or "").lower())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


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


def get_relevant_mhjh_context(message: str):
    """Return the single best MHJH knowledge answer, or ``None``.

    Matching is local and deterministic. Input and keywords are normalized so
    punctuation and common diacritics such as Hakkûh/Hakkuh do not break a hit.
    Longer keyword matches score higher and multiple matches accumulate.
    """
    q = _normalize(message)
    if not q:
        return None

    best_block = None
    best_score = 0

    for block in _load_mhjh_knowledge():
        score = 0
        for keyword in block.get("keywords", []):
            key = _normalize(keyword)
            if key and key in q:
                score += max(1, len(key.split()))

        if score > best_score:
            best_score = score
            best_block = block

    if not best_block:
        return None

    return best_block.get("answer")
