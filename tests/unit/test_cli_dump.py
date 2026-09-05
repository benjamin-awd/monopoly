"""Unit tests for `monopoly-fixture dump`.

Builds a trivial PDF in-process (no real statement) and checks that dump emits
pages.txt + metadata.json via the real parser, and writes no CSV.
"""

import json
from pathlib import Path

import pymupdf
from click.testing import CliRunner

from monopoly.cli.fixtures import fixtures


def _make_pdf(path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "HELLO WORLD STATEMENT\n12/01 COFFEE SHOP 1.23")
    doc.set_metadata({"producer": "TestProducer", "creator": "TestCreator"})
    doc.save(path)
    doc.close()


def test_dump_writes_pages_and_metadata(tmp_path):
    pdf = tmp_path / "statement.pdf"
    _make_pdf(pdf)
    out = tmp_path / "out"

    result = CliRunner().invoke(fixtures, ["dump", str(pdf), "--generic", "-o", str(out)])
    assert result.exit_code == 0, result.output

    page_files = sorted(out.glob("page_*.txt"))
    assert len(page_files) == 1
    assert "HELLO WORLD STATEMENT" in page_files[0].read_text()

    metadata = json.loads((out / "metadata.json").read_text())
    assert metadata["producer"] == "TestProducer"

    assert not list(out.glob("*.csv"))
    assert "Redact PII" in result.output


def test_dump_rejects_unknown_bank(tmp_path):
    pdf = tmp_path / "statement.pdf"
    _make_pdf(pdf)

    result = CliRunner().invoke(fixtures, ["dump", str(pdf), "--bank", "NotABank"])
    assert result.exit_code != 0
    assert "Unknown bank" in result.output


def test_dump_defaults_output_to_pdf_directory(tmp_path):
    pdf = tmp_path / "statement.pdf"
    _make_pdf(pdf)

    result = CliRunner().invoke(fixtures, ["dump", str(pdf), "--generic"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "page_01.txt").exists()
    assert (tmp_path / "metadata.json").exists()
