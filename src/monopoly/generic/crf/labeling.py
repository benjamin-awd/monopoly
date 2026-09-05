"""
Distant-supervision labeler for the CRF spike.

Turns the committed ``raw.csv`` gold rows (date, description, amount) into
per-token label sequences over ``{DATE, DESC, AMOUNT, BALANCE, O}`` by aligning
each gold row onto the statement line it best fits, then marking that line's
tokens. This is weak supervision: the labels are only as good as the fixture
gold, and the ceiling is bounded by fixture coverage (see the plan's Risks).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from .features import Token, amount_value, tokenize

# Re-exported under the old private name so existing callers keep working.
_amount_value = amount_value

LABELS = ("DATE", "DESC", "AMOUNT", "BALANCE", "O")

_WS_RE = re.compile(r"\s+")

# Largest token window checked when a gold date spans several tokens ("01 OCT").
_MAX_DATE_TOKENS = 4
# A line must clear this score to be claimed by a gold row (see ``_score``).
_MIN_MATCH_SCORE = 3.0
_AMOUNT_TOL = 0.005


@dataclass(frozen=True)
class GoldRow:
    """One expected transaction, as read from a fixture ``raw.csv``."""

    date: str
    description: str
    amount: float


def _norm(text: str) -> str:
    return _WS_RE.sub(" ", text).strip().lower()


def _mark_date(tokens: list[Token], labels: list[str], gold_date: str) -> None:
    target = _norm(gold_date)
    if not target:
        return
    n = len(tokens)
    for size in range(1, _MAX_DATE_TOKENS + 1):
        for start in range(n - size + 1):
            window = tokens[start : start + size]
            if _norm(" ".join(t.text for t in window)) == target:
                for k in range(start, start + size):
                    labels[k] = "DATE"
                return


def _mark_description(tokens: list[Token], labels: list[str], gold_desc: str) -> None:
    words = _norm(gold_desc).split()
    if not words:
        return
    wi = 0
    for k, tok in enumerate(tokens):
        if wi >= len(words):
            break
        if labels[k] == "O" and _norm(tok.text) == words[wi]:
            labels[k] = "DESC"
            wi += 1


def _mark_amounts(tokens: list[Token], labels: list[str], gold_amount: float) -> None:
    target = abs(gold_amount)
    amount_idx = [k for k, t in enumerate(tokens) if _amount_value(t.text) is not None]

    matched: int | None = None
    for k in amount_idx:
        value = _amount_value(tokens[k].text)
        if labels[k] == "O" and value is not None and math.isclose(value, target, abs_tol=_AMOUNT_TOL):
            labels[k] = "AMOUNT"
            matched = k
            break

    # A second money token (e.g. a running balance in a debit line) is BALANCE.
    if matched is not None:
        for k in amount_idx:
            if k != matched and labels[k] == "O":
                labels[k] = "BALANCE"
                break


def _label_tokens(tokens: list[Token], gold: GoldRow) -> list[str]:
    labels = ["O"] * len(tokens)
    _mark_date(tokens, labels, gold.date)
    _mark_description(tokens, labels, gold.description)
    _mark_amounts(tokens, labels, gold.amount)
    return labels


def label_line(line: str, gold: GoldRow) -> list[str]:
    """Label a single line already known to correspond to ``gold``."""
    return _label_tokens(tokenize(line), gold)


def _score(tokens: list[Token], gold: GoldRow) -> float:
    """How strongly a line matches a gold row: date + amount + description overlap."""
    score = 0.0

    target = _norm(gold.date)
    if target:
        for size in range(1, _MAX_DATE_TOKENS + 1):
            windows = (_norm(" ".join(t.text for t in tokens[s : s + size])) for s in range(len(tokens) - size + 1))
            if any(w == target for w in windows):
                score += 2.0
                break

    magnitude = abs(gold.amount)
    if any(
        (v := _amount_value(t.text)) is not None and math.isclose(v, magnitude, abs_tol=_AMOUNT_TOL) for t in tokens
    ):
        score += 2.0

    words = _norm(gold.description).split()
    if words:
        present = sum(1 for w in words if any(_norm(t.text) == w for t in tokens))
        score += 2.0 * present / len(words)

    return score


def label_page(lines: list[str], gold_rows: list[GoldRow]) -> list[list[str]]:
    """
    Label every line of a page.

    Each gold row claims the highest-scoring unused line above ``_MIN_MATCH_SCORE``;
    lines no gold row claims come back all-``O``. A gold row that matches nothing
    (e.g. a transaction split across pages) is skipped.
    """
    token_lines = [tokenize(line) for line in lines]
    labels: list[list[str]] = [["O"] * len(toks) for toks in token_lines]
    used: set[int] = set()

    for gold in gold_rows:
        best_idx: int | None = None
        best_score = _MIN_MATCH_SCORE
        for idx, tokens in enumerate(token_lines):
            if idx in used or not tokens:
                continue
            score = _score(tokens, gold)
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx is not None:
            used.add(best_idx)
            labels[best_idx] = _label_tokens(token_lines[best_idx], gold)

    return labels
