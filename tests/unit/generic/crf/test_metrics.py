"""Unit tests for the spike's metrics and heuristic baseline. Synthetic input only."""

from monopoly.generic.crf.evaluation import (
    detection_scores,
    heuristic_transaction_lines,
    token_f1,
    transaction_lines,
)

# A synthetic debit page: header, three dated transactions, a footer.
DEBIT_PAGE = [
    "STATEMENT OF ACCOUNT",
    "01 OCT   ValueVille SG      123.12     2,000.00",
    "02 OCT   CoffeePlace SG       9.80     1,990.20",
    "05 OCT   BookBarn SG         45.00     1,945.20",
    "TOTAL DUE",
]


def test_transaction_lines_from_labels():
    labeled = [["O"], ["DATE", "DESC", "AMOUNT"], ["O", "O"]]
    assert transaction_lines(labeled) == {1}


def test_token_f1_perfect():
    labels = [["DATE", "DESC", "AMOUNT"]]
    assert token_f1(labels, labels) == 1.0


def test_token_f1_penalises_a_missed_label():
    y_true = [["DATE", "DESC", "AMOUNT", "O"]]
    y_pred = [["DATE", "O", "AMOUNT", "O"]]  # DESC missed
    # tp=2 (DATE, AMOUNT), fn=1 (DESC), fp=0 -> P=1.0, R=2/3, F1=0.8
    assert abs(token_f1(y_true, y_pred) - 0.8) < 1e-9


def test_token_f1_penalises_a_confused_label():
    y_true = [["DATE", "AMOUNT"]]
    y_pred = [["AMOUNT", "AMOUNT"]]  # DATE confused for AMOUNT
    # tp=1 (AMOUNT), fp=1 (pred DATE->AMOUNT), fn=1 (true DATE) -> P=R=0.5, F1=0.5
    assert abs(token_f1(y_true, y_pred) - 0.5) < 1e-9


def test_detection_scores_overlap():
    score = detection_scores(gold={1, 2, 3}, predicted={2, 3, 4})
    assert abs(score.precision - 2 / 3) < 1e-9
    assert abs(score.recall - 2 / 3) < 1e-9


def test_detection_scores_both_empty_is_perfect():
    assert detection_scores(set(), set()).f1 == 1.0


def test_heuristic_detects_dated_transaction_lines():
    assert heuristic_transaction_lines(DEBIT_PAGE) == {1, 2, 3}


def test_heuristic_returns_empty_when_no_pattern():
    assert heuristic_transaction_lines(["NO DATES HERE", "JUST TEXT"]) == set()
