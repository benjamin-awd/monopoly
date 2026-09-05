"""Unit tests for `monopoly-fixture render`.

Renders a committed text fixture into a synthetic PDF and checks that the PDF
exists and has one page per page_*.txt file. Fidelity of the round-trip (that
the pipeline still extracts transactions) is covered by the integration test
tests/integration/test_render_roundtrip.py.
"""

from pathlib import Path

import pymupdf
from click.testing import CliRunner

from monopoly.cli.fixtures import fixtures

# dbs/credit is a committed multi-page fixture that exercises the page-count assertion.
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "integration" / "banks" / "dbs" / "credit"


def test_render_writes_pdf_with_one_page_per_text_page(tmp_path):
    out = tmp_path / "rendered.pdf"

    result = CliRunner().invoke(fixtures, ["render", str(FIXTURE_DIR), "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()

    expected_pages = len(list(FIXTURE_DIR.glob("page_*.txt")))
    with pymupdf.open(str(out)) as doc:
        assert doc.page_count == expected_pages


def test_render_defaults_output_to_directory(tmp_path):
    # copy the committed page files into a writable dir so the default output
    # path (<directory>/rendered.pdf) lands somewhere temporary.
    for page in sorted(FIXTURE_DIR.glob("page_*.txt")):
        (tmp_path / page.name).write_text(page.read_text(encoding="utf8"), encoding="utf8")

    result = CliRunner().invoke(fixtures, ["render", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "rendered.pdf").exists()
