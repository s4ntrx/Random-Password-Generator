"""Cryptographically secure password generation (uses `secrets`, not `random`)."""
from __future__ import annotations

import math
import secrets
import string
from dataclasses import dataclass

MIN_LENGTH = 4
MAX_LENGTH = 128
AMBIGUOUS_CHARS = frozenset("Il1O0o")


@dataclass(frozen=True)
class Options:
    length: int = 16
    lowercase: bool = True
    uppercase: bool = True
    digits: bool = True
    symbols: bool = True
    exclude_ambiguous: bool = False

    def character_sets(self) -> list[str]:
        candidates = (
            (self.lowercase, string.ascii_lowercase),
            (self.uppercase, string.ascii_uppercase),
            (self.digits, string.digits),
            (self.symbols, string.punctuation),
        )
        sets = []
        for enabled, characters in candidates:
            if not enabled:
                continue
            if self.exclude_ambiguous:
                characters = "".join(c for c in characters if c not in AMBIGUOUS_CHARS)
            sets.append(characters)
        return sets


def generate_password(options: Options = Options()) -> str:
    """Return a password with at least one character from every enabled set."""
    character_sets = options.character_sets()
    if not character_sets:
        raise ValueError("Select at least one character set.")
    if not MIN_LENGTH <= options.length <= MAX_LENGTH:
        raise ValueError(f"Length must be between {MIN_LENGTH} and {MAX_LENGTH}.")

    all_characters = "".join(character_sets)
    password = [secrets.choice(chars) for chars in character_sets]
    password += [secrets.choice(all_characters) for _ in range(options.length - len(password))]
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def entropy_bits(options: Options) -> float:
    """Upper-bound entropy estimate: length * log2(pool size)."""
    pool_size = len(set("".join(options.character_sets())))
    return options.length * math.log2(pool_size) if pool_size else 0.0


def strength_label(bits: float) -> str:
    for limit, label in ((40, "Weak"), (60, "Fair"), (80, "Strong")):
        if bits < limit:
            return label
    return "Very strong"
