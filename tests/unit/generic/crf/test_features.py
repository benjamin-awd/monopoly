"""Unit tests for the CRF featurizer. Synthetic lines only -- no fixtures, no PII."""

import pytest

from monopoly.generic.crf.features import (
    Token,
    amount_value,
    line_features,
    token_features,
    tokenize,
)

# A representative debit line: date, description, amount, running balance.
DEBIT_LINE = "01 OCT   ValueVille SG      123.12     2,000.00"


def test_tokenize_preserves_offsets():
    tokens = tokenize("01 OCT  9.80")
    assert tokens == [
        Token("01", 0, 2),
        Token("OCT", 3, 6),
        Token("9.80", 8, 12),
    ]
    # offsets index back into the original string
    line = "01 OCT  9.80"
    assert all(line[t.start : t.end] == t.text for t in tokens)


def test_tokenize_empty_line():
    assert tokenize("") == []
    assert tokenize("     ") == []


def test_amount_tokens_flagged():
    feats = {f["tok.lower"]: f for f in line_features(DEBIT_LINE)}
    assert feats["123.12"]["tok.is_amount"] is True
    assert feats["2,000.00"]["tok.is_amount"] is True
    # a bare day-of-month integer is not money
    assert feats["01"]["tok.is_amount"] is False


def test_month_and_currency_flags():
    feats = {f["tok.lower"]: f for f in line_features("15 October  DBS SGD  9.80")}
    assert feats["october"]["tok.is_month"] is True
    assert feats["sgd"]["tok.is_currency"] is True
    # a plain word is neither
    assert feats["dbs"]["tok.is_month"] is False
    assert feats["dbs"]["tok.is_currency"] is False


def test_abbreviated_month_flag():
    feats = line_features("01 OCT  9.80")
    assert feats[1]["tok.lower"] == "oct"
    assert feats[1]["tok.is_month"] is True


def test_line_boundary_and_position_features():
    feats = line_features(DEBIT_LINE)
    # first token carries BOS and is flagged line-start; last carries EOS.
    assert feats[0]["pos.is_line_start"] is True
    assert feats[0].get("BOS") is True
    assert feats[-1]["pos.is_line_end"] is True
    assert feats[-1].get("EOS") is True
    # relative start position increases left-to-right and is normalized to [0, 1].
    rel_starts = [f["pos.rel_start"] for f in feats]
    assert rel_starts == sorted(rel_starts)
    assert all(0.0 <= r <= 1.0 for r in rel_starts)


def test_context_features_reference_neighbours():
    feats = line_features(DEBIT_LINE)
    # the balance (last token) sees the preceding amount as its left neighbour.
    last = feats[-1]
    assert last["-1.is_amount"] is True
    assert "+1.lower" not in last  # nothing to the right of the last token


def test_single_token_line_has_bos_and_eos():
    feats = line_features("9.80")
    assert len(feats) == 1
    assert feats[0].get("BOS") is True
    assert feats[0].get("EOS") is True
    assert feats[0]["pos.is_line_start"] is True
    assert feats[0]["pos.is_line_end"] is True


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("120.00-", 120.0),  # Maybank trailing minus
        ("300.00+", 300.0),  # Maybank trailing plus
        ("5'200.00", 5200.0),  # ZKB apostrophe thousands separator
        ("1'320.75", 1320.75),
        ("60.00CR", 60.0),  # HSBC glued credit marker
        ("500.00CR", 500.0),
        ("1,234.50DR", 1234.5),  # glued debit marker + comma thousands
        ("(500.00)", 500.0),  # parenthesised negative
        ("2,000.00", 2000.0),  # comma thousands
        ("9.80", 9.80),
        ("20", None),  # bare day-of-month integer is not money
        ("03.09.2025", None),  # a date is not an amount
    ],
)
def test_amount_value_handles_statement_variants(token, expected):
    assert amount_value(token) == expected


def test_trailing_sign_token_flagged_is_amount():
    feats = {f["tok.lower"]: f for f in line_features("01/08/23  CASH   120.00-   380.00")}
    assert feats["120.00-"]["tok.is_amount"] is True


def test_token_features_index_bounds():
    tokens = tokenize(DEBIT_LINE)
    first = token_features(tokens, 0, len(DEBIT_LINE))
    assert first["pos.index"] == 0
    assert first["bias"] == 1.0
