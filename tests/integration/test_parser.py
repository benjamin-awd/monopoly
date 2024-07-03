from pathlib import Path

from pytest import raises

from monopoly.pdf import PdfDocument, PdfParser

fixture_directory = Path(__file__).parent / "fixtures"


def test_get_pages(parser: PdfParser, pdf_document: PdfDocument):
    pdf_document.file_path = fixture_directory / "4_pages_blank.pdf"
    parser.document = pdf_document
    parser.page_range = slice(0, -1)

    pages = parser.get_pages()
    assert len(pages) == 3


def test_get_pages_invalid_returns_error(parser: PdfParser, pdf_document: PdfDocument):
    pdf_document.file_path = fixture_directory / "4_pages_blank.pdf"
    parser.document = pdf_document
    parser.page_range = slice(99, -99)

    with raises(ValueError, match="bad page number"):
        parser.get_pages()
