"""
Pure feature extraction for the CRF token classifier (offline spike).

No model dependency lives here -- this module turns a statement line into
per-token feature dicts that ``sklearn-crfsuite`` / ``pycrfsuite`` consume.

Positional features use the *character offset* of each token within the
physical-layout line, which is the only geometry the generic parser has (see the
plan's Problem section). True ``(x, y)`` coordinates are a deliberate follow-up,
not part of this spike.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from monopoly.constants.date import DateFormats

# An amount must carry a thousands separator or a decimal part, so bare small
# integers like a day-of-month ("20") are not misread as money. Real statements
# vary the surface form, so allow: a leading sign or "(" (parenthesised negative);
# ",", "'" (Swiss/ZKB), U+2019, or space thousands separators; and a *trailing*
# sign (Maybank prints "120.00-"/"300.00+") or ")".
# Thousands separators seen across banks: comma, ASCII apostrophe (Swiss/ZKB
# prints "5'200.00"), and space. Amounts may also carry a trailing sign or a
# glued CR/DR direction marker (HSBC prints "60.00CR"/"500.00CR").
_THOUSANDS = r"[,' ]"
_AMOUNT_RE = re.compile(
    rf"^[-+(]?(?:\d{{1,3}}(?:{_THOUSANDS}\d{{3}})+(?:\.\d{{1,2}})?|\d+\.\d{{1,2}})[)+\-]?(?i:cr|dr)?$"
)
_AMOUNT_STRIP_RE = re.compile(r"[,' ]")
_AMOUNT_SUFFIX_RE = re.compile(r"(?i)(?:cr|dr)$")
_MONTH_RE = re.compile(rf"(?:{DateFormats.MMM}|{DateFormats.MMMM})")
_DIGIT_RE = re.compile(r"\d")
_TOKEN_RE = re.compile(r"\S+")

# ISO 4217 codes common to the supported banks; membership is a stronger signal
# than the bare three-uppercase-letters shape.
COMMON_CURRENCIES = frozenset(
    {
        "SGD",
        "USD",
        "EUR",
        "GBP",
        "CHF",
        "JPY",
        "AUD",
        "CAD",
        "HKD",
        "CNY",
        "MYR",
        "THB",
        "INR",
        "NZD",
    }
)

# Width of the character-offset bucket used as a coarse column signal.
COL_BUCKET = 8

# Fields copied from a neighbour token into the current token's context features.
_CONTEXT_FIELDS = ("lower", "is_amount", "is_month", "has_digit", "is_currency")


@dataclass(frozen=True)
class Token:
    """A whitespace-delimited token and its character span within a line."""

    text: str
    start: int
    end: int


def tokenize(line: str) -> list[Token]:
    """Split a line into whitespace-delimited tokens, preserving char offsets."""
    return [Token(m.group(), m.start(), m.end()) for m in _TOKEN_RE.finditer(line)]


def amount_value(text: str) -> float | None:
    """
    Return the magnitude of an amount token, or ``None`` if it is not an amount.

    Handles the surface variants in real statements (leading/trailing sign,
    parenthesised negatives, ``,``/``'``/space thousands separators); the sign is
    dropped since only magnitude is used for matching.
    """
    if not _AMOUNT_RE.fullmatch(text):
        return None
    cleaned = _AMOUNT_STRIP_RE.sub("", text).replace("(", "").replace(")", "")
    cleaned = _AMOUNT_SUFFIX_RE.sub("", cleaned).rstrip("+-")
    try:
        return abs(float(cleaned))
    except ValueError:
        return None


def _shape(text: str) -> dict[str, Any]:
    """Lexical, position-independent features for a single token's text."""
    lower = text.lower()
    return {
        "lower": lower,
        "prefix2": lower[:2],
        "suffix3": lower[-3:],
        "is_upper": text.isupper(),
        "is_title": text.istitle(),
        "is_digit": text.isdigit(),
        "has_digit": bool(_DIGIT_RE.search(text)),
        "is_amount": bool(_AMOUNT_RE.fullmatch(text)),
        "is_month": bool(_MONTH_RE.fullmatch(text)),
        # Membership in the known ISO 4217 set, not a bare three-uppercase shape:
        # acronyms like "DBS"/"ATM" would otherwise be misread as currency codes.
        "is_currency": text in COMMON_CURRENCIES,
        "word_len": len(text),
        "has_comma": "," in text,
        "has_dot": "." in text,
        "has_slash": "/" in text,
    }


def token_features(tokens: list[Token], i: int, line_length: int) -> dict[str, Any]:
    """Feature dict for the token at index ``i``: shape + char-offset + context."""
    tok = tokens[i]
    feats: dict[str, Any] = {"bias": 1.0}

    for key, value in _shape(tok.text).items():
        feats[f"tok.{key}"] = value

    # Positional features: char-offset proxy for column geometry.
    denom = max(line_length, 1)
    feats["pos.rel_start"] = tok.start / denom
    feats["pos.col_bucket"] = str(tok.start // COL_BUCKET)
    feats["pos.is_line_start"] = i == 0
    feats["pos.is_line_end"] = i == len(tokens) - 1
    feats["pos.index"] = i

    # Context features from the immediate neighbours.
    if i > 0:
        prev = _shape(tokens[i - 1].text)
        for key in _CONTEXT_FIELDS:
            feats[f"-1.{key}"] = prev[key]
    else:
        feats["BOS"] = True

    if i < len(tokens) - 1:
        nxt = _shape(tokens[i + 1].text)
        for key in _CONTEXT_FIELDS:
            feats[f"+1.{key}"] = nxt[key]
    else:
        feats["EOS"] = True

    return feats


def line_features(line: str) -> list[dict[str, Any]]:
    """Feature dicts for every token in a line, in reading order."""
    tokens = tokenize(line)
    return [token_features(tokens, i, len(line)) for i in range(len(tokens))]
