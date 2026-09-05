"""
Metrics and the heuristic baseline for the CRF spike.

Deliberately free of the ``crf`` extra: it operates on label matrices (which the
CRF or the labeler produce) and on the *existing* generic heuristic, so the
comparison is apples-to-apples and this module imports without sklearn-crfsuite.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from monopoly.generic.generic import DatePatternAnalyzer, GenericParserError
from monopoly.identifiers import MetadataIdentifier
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)

# Labels that mark real transaction content (everything but the "O" outside label).
CONTENT_LABELS = ("DATE", "DESC", "AMOUNT", "BALANCE")
# A line counts as a transaction if an amount was found on it.
_TRANSACTION_LABEL = "AMOUNT"


@dataclass(frozen=True)
class DetectionScore:
    """Precision/recall/F1 for which *lines* were identified as transactions."""

    precision: float
    recall: float
    f1: float


def transaction_lines(labeled: list[list[str]]) -> set[int]:
    """Return indices of lines whose label sequence marks a transaction (has an amount)."""
    return {i for i, labels in enumerate(labeled) if _TRANSACTION_LABEL in labels}


def heuristic_transaction_lines(lines: list[str]) -> set[int]:
    """
    Baseline: lines the *current* generic parser would treat as transactions.

    Runs ``DatePatternAnalyzer`` over the page and matches its synthesized
    transaction regex against each line -- the same signal the live parser uses
    to find the first transaction. Returns an empty set if no pattern is found.
    """
    page = PdfPage(raw_text="\n".join(lines))
    try:
        analyzer = DatePatternAnalyzer([page], MetadataIdentifier())
        pattern = analyzer.create_transaction_pattern()
    except (GenericParserError, ValueError) as err:
        logger.debug("Heuristic found no transaction pattern: %s", err)
        return set()
    return {i for i, line in enumerate(lines) if pattern.search(line)}


def detection_scores(gold: set[int], predicted: set[int]) -> DetectionScore:
    """Line-level precision/recall/F1 of ``predicted`` against ``gold``."""
    if not predicted and not gold:
        return DetectionScore(1.0, 1.0, 1.0)
    true_positives = len(gold & predicted)
    precision = true_positives / len(predicted) if predicted else 0.0
    recall = true_positives / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return DetectionScore(precision, recall, f1)


def token_f1(y_true: list[list[str]], y_pred: list[list[str]]) -> float:
    """
    Micro-averaged token F1 over content labels (``O`` excluded).

    Computed by hand to avoid pulling in ``sklearn_crfsuite.metrics`` (and thus
    the extra); micro-F1 over the non-``O`` labels is the number we care about.
    """
    tp = fp = fn = 0
    for true_seq, pred_seq in zip(y_true, y_pred, strict=True):
        for true_label, pred_label in zip(true_seq, pred_seq, strict=True):
            true_content = true_label in CONTENT_LABELS
            pred_content = pred_label in CONTENT_LABELS
            if true_content and pred_label == true_label:
                tp += 1
            elif pred_content and pred_label != true_label:
                fp += 1
                if true_content:
                    fn += 1
            elif true_content:
                fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
