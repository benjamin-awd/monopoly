"""
Unit tests for the fixture adapter.

The mini fixture is built in ``tmp_path`` at runtime rather than committed: a
``raw.csv`` under ``tests/unit`` would be swallowed by the repo's ``*.csv``
gitignore (only ``tests/integration/banks`` is excepted), so a committed copy
would pass locally and vanish in CI.
"""

from pathlib import Path

import pytest

from monopoly.generic.crf.fixtures import (
    iter_fixture_dirs,
    load_fixture,
    read_gold_rows,
    read_pages,
)
from monopoly.generic.crf.labeling import GoldRow, label_page

PAGE_TEXT = """\
SYNTHETIC BANK STATEMENT
ACCOUNT SUMMARY
 03/07          SAMPLE COFFEE HOUSE   SG              10.00
 05/07          EXAMPLE GROCER        SG              20.00
END OF STATEMENT
"""

RAW_CSV_TEXT = """\
date,description,amount
03/07,SAMPLE COFFEE HOUSE SG,-10.0
05/07,EXAMPLE GROCER SG,-20.0
"""


@pytest.fixture
def mini_fixture(tmp_path: Path) -> Path:
    fixture_dir = tmp_path / "banks" / "synthetic" / "credit"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "page_01.txt").write_text(PAGE_TEXT)
    (fixture_dir / "raw.csv").write_text(RAW_CSV_TEXT)
    return fixture_dir


def test_read_gold_rows_parses_raw_csv(mini_fixture: Path):
    assert read_gold_rows(mini_fixture) == [
        GoldRow("03/07", "SAMPLE COFFEE HOUSE SG", -10.0),
        GoldRow("05/07", "EXAMPLE GROCER SG", -20.0),
    ]


def test_read_pages_returns_lines_in_order(mini_fixture: Path):
    lines = read_pages(mini_fixture)
    assert lines[0] == "SYNTHETIC BANK STATEMENT"
    assert any("SAMPLE COFFEE HOUSE" in line for line in lines)


def test_load_fixture_feeds_the_labeler_end_to_end(mini_fixture: Path):
    lines, gold = load_fixture(mini_fixture)
    labeled = label_page(lines, gold)

    # exactly the two transaction lines carry DATE + AMOUNT; the rest are all-O.
    labeled_lines = [i for i, labs in enumerate(labeled) if set(labs) != {"O"}]
    assert len(labeled_lines) == 2
    for i in labeled_lines:
        assert "DATE" in labeled[i]
        assert "AMOUNT" in labeled[i]


def test_iter_fixture_dirs_discovers_only_complete_fixtures(mini_fixture: Path):
    root = mini_fixture.parents[1]  # .../banks
    # a sibling dir with pages but no raw.csv must be ignored
    incomplete = root / "incomplete" / "credit"
    incomplete.mkdir(parents=True)
    (incomplete / "page_01.txt").write_text("NOTHING HERE\n")

    found = iter_fixture_dirs(root)
    assert mini_fixture in found
    assert incomplete not in found
