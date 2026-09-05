"""Render round-trip fidelity gate for `monopoly-fixture render`.

The performance workflows benchmark `monopoly` over PDFs rendered from the
committed page_*.txt fixtures. A lossy monospace re-render could shift columns
and make extraction bail early (especially for debit statements, where amounts
are classified into withdrawal/deposit columns by position). This test renders
a representative set, runs the *real* pipeline on the rendered PDF, and asserts
transactions are extracted - proving the fixed-pitch grid preserves the columns
the bank regexes depend on.
"""

from pathlib import Path

import pytest

from monopoly.banks import Dbs, Ocbc
from monopoly.cli.fixtures import _read_pages, _render_pages_to_pdf
from monopoly.pdf import PdfDocument, PdfParser
from monopoly.pipeline import Pipeline

BANKS_DIR = Path(__file__).parent / "banks"

# Keep at least one debit fixture (column-classified) in the set - that is the
# layout most sensitive to a lossy round-trip.
roundtrip_cases = [
    (Dbs, "credit"),
    (Dbs, "debit"),
    (Ocbc, "debit"),
]


@pytest.mark.parametrize("bank, statement_type", roundtrip_cases)
def test_render_roundtrip_extracts_transactions(bank, statement_type, tmp_path):
    fixture_dir = BANKS_DIR / bank.name / statement_type
    rendered = tmp_path / f"{bank.name}_{statement_type}.pdf"

    document = _render_pages_to_pdf(_read_pages(fixture_dir))
    document.save(str(rendered))
    document.close()

    pdf_document = PdfDocument(file_path=rendered)
    statement = Pipeline(PdfParser(bank, pdf_document)).extract()

    assert statement.transactions, "no transactions extracted from rendered PDF"
    assert statement.perform_safety_check()
