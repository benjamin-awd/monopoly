"""
Integration guard for the CRF spike's leave-one-bank-out harness.

Runs over the committed synthetic ``page_NN.txt`` + ``raw.csv`` fixtures (no PII,
no git-crypt), asserts the sweep completes for every fixture with in-range
scores, and prints the CRF-vs-heuristic table for the record. Skips cleanly if
the optional ``crf`` extra is not installed.
"""

from pathlib import Path

import pytest

pytest.importorskip("sklearn_crfsuite")

from monopoly.generic.crf.fixtures import iter_fixture_dirs  # noqa: E402
from monopoly.generic.crf.spike import format_table, run_leave_one_out  # noqa: E402

BANKS_ROOT = Path(__file__).parents[1] / "banks"


def test_leave_one_out_runs_for_every_fixture(capsys):
    expected = iter_fixture_dirs(BANKS_ROOT)
    assert expected, "no bank fixtures discovered"

    results = run_leave_one_out(BANKS_ROOT)

    # the sweep produced one result per discovered fixture
    assert len(results) == len(expected)

    for result in results:
        for score in (result.crf, result.heuristic):
            assert 0.0 <= score.precision <= 1.0
            assert 0.0 <= score.recall <= 1.0
            assert 0.0 <= score.f1 <= 1.0
        assert 0.0 <= result.crf_token_f1 <= 1.0

    # the CRF must actually learn *something* across the corpus, or the pipeline
    # (features/labels/model) is broken -- this is a smoke floor, not a quality bar.
    mean_token_f1 = sum(r.crf_token_f1 for r in results) / len(results)
    assert mean_token_f1 > 0.0

    # surface the comparison table in captured output for the record.
    with capsys.disabled():
        print("\n" + format_table(results))
