from __future__ import annotations

import secrets


ADJECTIVES = [
    "amber",
    "mango",
    "violet",
    "silver",
    "quiet",
    "gentle",
    "bright",
    "copper",
    "lunar",
    "river",
]
NOUNS = [
    "river",
    "harbor",
    "cloud",
    "lantern",
    "bamboo",
    "meadow",
    "harvest",
    "forest",
    "canyon",
    "anchor",
]
PHRASE_WORDS = [
    "silver",
    "bamboo",
    "quiet",
    "lantern",
    "amber",
    "cloud",
    "gentle",
    "harbor",
    "lunar",
    "meadow",
]


def generate_transfer_id() -> str:
    return f"tr_{secrets.token_urlsafe(8)}"


def generate_short_code() -> str:
    adjective = secrets.choice(ADJECTIVES)
    noun = secrets.choice(NOUNS)
    suffix = secrets.randbelow(90) + 10
    return f"{adjective}-{noun}-{suffix}"


def generate_confirm_phrase() -> str:
    first = secrets.choice(PHRASE_WORDS)
    second = secrets.choice([word for word in PHRASE_WORDS if word != first])
    return f"{first} {second}"
