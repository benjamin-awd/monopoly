"""Unit tests for building a PdfParser from pre-extracted page text.

These exercise the text-fixture path: a parser built with no PDF at all, only
raw page text, which the pipeline can still extract from. No file on disk and no
pdftotext call is involved.
"""

from pathlib import Path

from monopoly.examples.example_bank import ExampleBank
from monopoly.identifiers import MetadataIdentifier
from monopoly.pdf import PdfPage, PdfParser
from monopoly.pipeline import Pipeline

# Hand-written text shaped to match ExampleBank's credit config: a statement
# date, a header line, and two transaction lines.
SAMPLE_PAGE = "01-02-2024\nDATE DESCRIPTION AMOUNT\n12/01 COFFEE SHOP 12.34\n13/01 BOOK STORE 56.78\n"


def test_from_pages_extracts_without_a_pdf():
    parser = PdfParser.from_pages(ExampleBank, [SAMPLE_PAGE])

    assert parser.document is None
    assert isinstance(parser.pages[0], PdfPage)

    statement = Pipeline(parser).extract(safety_check=False)

    assert [tx.description for tx in statement.transactions] == ["COFFEE SHOP", "BOOK STORE"]
    assert [abs(tx.amount) for tx in statement.transactions] == [12.34, 56.78]


def test_from_pages_accepts_prebuilt_pages():
    pages = [PdfPage(SAMPLE_PAGE)]
    parser = PdfParser.from_pages(ExampleBank, pages)

    assert parser.pages == pages


def test_from_pages_carries_file_path_and_metadata():
    parser = PdfParser.from_pages(
        ExampleBank,
        [SAMPLE_PAGE],
        metadata=MetadataIdentifier(producer="Redacted Producer"),
        file_path=Path("redacted.txt"),
    )

    assert parser.file_path == Path("redacted.txt")
    assert parser.metadata_identifier.producer == "Redacted Producer"

    # the handler picks up the file path from the parser, not a live document
    pipeline = Pipeline(parser)
    assert pipeline.handler.file_path == Path("redacted.txt")


def test_from_pages_defaults_file_path_and_metadata_to_none():
    parser = PdfParser.from_pages(ExampleBank, [SAMPLE_PAGE])

    assert parser.file_path is None
    assert parser.metadata_identifier == MetadataIdentifier()
