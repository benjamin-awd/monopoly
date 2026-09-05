"""
Leave-one-bank-out harness: CRF vs the current heuristic on the bank fixtures.

For each fixture, train a CRF on every *other* fixture's distant-supervised
labels, then compare -- on the held-out fixture -- which lines each approach
calls a transaction (against the ``raw.csv`` gold). Prints a per-fixture table;
run it directly for a local report:

    python -m monopoly.generic.crf.spike tests/integration/banks

This measures the spike's go/no-go signal. It does not touch live extraction.
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from .evaluation import (
    DetectionScore,
    detection_scores,
    heuristic_transaction_lines,
    token_f1,
    transaction_lines,
)
from .features import line_features
from .fixtures import iter_fixture_dirs, load_fixture
from .labeling import label_page
from .model import TransactionCRF

logger = logging.getLogger(__name__)

# Fewer iterations than the default keep the leave-one-out sweep quick in CI.
_HARNESS_PARAMS = {"max_iterations": 100}


@dataclass(frozen=True)
class FixtureResult:
    """One held-out fixture's CRF and heuristic line-detection scores."""

    name: str
    crf: DetectionScore
    heuristic: DetectionScore
    crf_token_f1: float


@dataclass(frozen=True)
class _LabeledFixture:
    lines: list[str]
    labels: list[list[str]]


def _labeled(fixture_dir: Path) -> _LabeledFixture:
    lines, gold = load_fixture(fixture_dir)
    return _LabeledFixture(lines, label_page(lines, gold))


def _training_pairs(data: dict[Path, _LabeledFixture], held_out: Path) -> tuple[list[list[dict]], list[list[str]]]:
    features: list[list[dict]] = []
    labels: list[list[str]] = []
    for fixture_dir, fixture in data.items():
        if fixture_dir == held_out:
            continue
        for line, line_labels in zip(fixture.lines, fixture.labels, strict=True):
            if not line.strip():
                continue
            features.append(line_features(line))
            labels.append(line_labels)
    return features, labels


def run_leave_one_out(root: Path, **crf_params: object) -> list[FixtureResult]:
    """Train per held-out fixture and score CRF vs heuristic on it."""
    fixture_dirs = iter_fixture_dirs(root)
    data = {fixture_dir: _labeled(fixture_dir) for fixture_dir in fixture_dirs}

    results: list[FixtureResult] = []
    for held_out in fixture_dirs:
        features, labels = _training_pairs(data, held_out)
        crf = TransactionCRF(**{**_HARNESS_PARAMS, **crf_params}).train(features, labels)

        fixture = data[held_out]
        gold_lines = transaction_lines(fixture.labels)

        predicted_labels = [crf.predict_line(line) if line.strip() else [] for line in fixture.lines]
        crf_lines = transaction_lines(predicted_labels)

        results.append(
            FixtureResult(
                name=held_out.relative_to(root).as_posix(),
                crf=detection_scores(gold_lines, crf_lines),
                heuristic=detection_scores(gold_lines, heuristic_transaction_lines(fixture.lines)),
                crf_token_f1=token_f1(fixture.labels, predicted_labels),
            )
        )
    return results


def _format_row(name: str, crf: DetectionScore, heuristic: DetectionScore, crf_token_f1: float) -> str:
    return (
        f"{name:<26} "
        f"{crf.recall:>8.2f} {crf.precision:>8.2f} "
        f"{heuristic.recall:>8.2f} {heuristic.precision:>9.2f} "
        f"{crf_token_f1:>9.2f}"
    )


def format_table(results: list[FixtureResult]) -> str:
    """Render the results as a fixed-width CRF-vs-heuristic comparison table."""
    header = f"{'fixture':<26} {'crf_rec':>8} {'crf_prec':>8} {'heur_rec':>8} {'heur_prec':>9} {'crf_tokF1':>9}"
    rows = [header, "-" * len(header)]
    rows.extend(_format_row(r.name, r.crf, r.heuristic, r.crf_token_f1) for r in results)
    count = len(results)
    if count:
        mean_crf = DetectionScore(
            precision=sum(r.crf.precision for r in results) / count,
            recall=sum(r.crf.recall for r in results) / count,
            f1=sum(r.crf.f1 for r in results) / count,
        )
        mean_heuristic = DetectionScore(
            precision=sum(r.heuristic.precision for r in results) / count,
            recall=sum(r.heuristic.recall for r in results) / count,
            f1=sum(r.heuristic.f1 for r in results) / count,
        )
        mean_token_f1 = sum(r.crf_token_f1 for r in results) / count
        rows.append("-" * len(header))
        rows.append(_format_row("MEAN", mean_crf, mean_heuristic, mean_token_f1))
    return "\n".join(rows)


def main() -> None:
    """Run the harness over a fixtures root given on the command line."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tests/integration/banks")
    logger.info(format_table(run_leave_one_out(root)))


if __name__ == "__main__":
    main()
