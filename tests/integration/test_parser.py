from pathlib import Path

from pytest import raises

from monopoly.pdf import MissingOCRError, PdfDocument, PdfParser

fixture_directory = Path(__file__).parent / "fixtures"


def test_get_pages(parser: PdfParser):
    pdf_document = PdfDocument(file_path="src/monopoly/examples/example_statement.pdf")
    parser.document = pdf_document
    parser.page_range = slice(0, -1)
    assert len(parser._get_pages()) == 3


def test_get_pages_with_no_text(parser: PdfParser):
    pdf_document = PdfDocument(file_path=fixture_directory / "4_pages_blank.pdf")
    parser.document = pdf_document
    parser.page_range = slice(0, -1)

    with raises(MissingOCRError):
        parser._get_pages()


def test_get_pages_invalid_returns_error(parser: PdfParser):
    pdf_document = PdfDocument(file_path=fixture_directory / "4_pages_blank.pdf")
    parser.document = pdf_document
    parser.page_range = slice(99, -99)

    with raises(ValueError, match="bad page number"):
        parser._get_pages()
