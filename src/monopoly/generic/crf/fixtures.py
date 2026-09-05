"""
Read committed bank fixtures into the labeler's inputs.

Pairs a fixture directory's ``page_NN.txt`` text with its ``raw.csv`` gold rows,
so the CRF spike trains and evaluates over the synthetic, non-PII fixtures under
``tests/integration/banks/`` (CLAUDE.md: bank fixtures are synthetic).
"""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING

from monopoly.constants import Columns

from .labeling import GoldRow

if TYPE_CHECKING:
    from pathlib import Path

PAGE_GLOB = "page_*.txt"
RAW_CSV = "raw.csv"


def read_pages(fixture_dir: Path) -> list[str]:
    """All lines of a fixture's pages, in page-then-line order."""
    lines: list[str] = []
    for page_path in sorted(fixture_dir.glob(PAGE_GLOB)):
        lines.extend(page_path.read_text().splitlines())
    return lines


def read_gold_rows(fixture_dir: Path) -> list[GoldRow]:
    """Gold transactions from a fixture's ``raw.csv``."""
    with (fixture_dir / RAW_CSV).open() as handle:
        return [
            GoldRow(
                date=row[Columns.DATE],
                description=row[Columns.DESCRIPTION],
                amount=float(row[Columns.AMOUNT]),
            )
            for row in csv.DictReader(handle)
        ]


def load_fixture(fixture_dir: Path) -> tuple[list[str], list[GoldRow]]:
    """Return a fixture's page lines paired with its gold rows."""
    return read_pages(fixture_dir), read_gold_rows(fixture_dir)


def iter_fixture_dirs(root: Path) -> list[Path]:
    """Fixture dirs under ``root`` that have both page text and a ``raw.csv``."""
    candidates = {csv_path.parent for csv_path in root.rglob(RAW_CSV)}
    return sorted(d for d in candidates if any(d.glob(PAGE_GLOB)))
