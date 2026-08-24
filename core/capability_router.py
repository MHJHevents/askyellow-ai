"""Lightweight capability routing for Yello Core.

Keep this deterministic and cheap. The router decides which capability owns a
request; it does not answer the request itself.
"""

SHOPPING_ACTION_TRIGGERS = (
    "zoek voor mij",
    "zoek me",
    "zoek een",
    "zoek de",
    "ik wil kopen",
    "wil kopen",
    "kopen",
    "bestellen",
    "waar kan ik",
    "waar koop ik",
    "vergelijk",
    "vergelijken",
    "prijs",
    "prijzen",
    "budget",
    "onder €",
    "tot €",
    "max €",
    "maximaal €",
    "euro",
)

PRODUCT_NOUNS = (
    "stofzuiger", "wasmachine", "droger", "vaatwasser", "airfryer",
    "tv", "televisie", "koptelefoon", "oortjes", "speaker", "soundbar",
    "laptop", "computer", "telefoon", "smartphone", "tablet", "monitor",
    "fiets", "fatbike", "boormachine", "gereedschap",
    "schoenen", "jas", "broek", "trui", "jurk", "tas", "horloge",
    "cadeau", "speelgoed", "lego", "scheerapparaat", "trimmer",
)


def detect_capability(message: str) -> str:
    """Return ``shopper`` only for actionable shopping intent.

    A general advice question such as "wat is een goede stofzuiger?" remains a
    YellowMind chat. A request with a buy/search/compare/budget signal plus a
    recognisable product is routed to the cold Shopper capability.
    """
    q = (message or "").lower().strip()
    if not q:
        return "yellowmind"

    has_action = any(trigger in q for trigger in SHOPPING_ACTION_TRIGGERS)
    has_product = any(noun in q for noun in PRODUCT_NOUNS)

    if has_action and has_product:
        return "shopper"

    return "yellowmind"
