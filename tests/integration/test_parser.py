from pytest import raises

from monopoly.banks import Hsbc
from monopoly.pdf import PdfParser


def test_can_open_protected(parser: PdfParser):
    parser.file_path = "tests/integration/fixtures/protected.pdf"
    parser.password = "foobar123"

    parser.open()


def test_wrong_password_raises_error(parser: PdfParser):
    parser.file_path = "tests/integration/fixtures/protected.pdf"
    parser.password = "wrong_pw"

    with raises(ValueError, match="Wrong password"):
        parser.open()


def test_get_pages(parser: PdfParser):
    parser.file_path = "tests/integration/fixtures/4_pages_blank.pdf"
    parser.page_range = slice(0, -1)

    pages = parser.get_pages()
    assert len(pages) == 3


def test_get_pages_invalid_returns_error(parser: PdfParser):
    parser.file_path = "tests/integration/fixtures/4_pages_blank.pdf"
    parser.page_range = slice(99, -99)

    with raises(ValueError, match="bad page number"):
        parser.get_pages()


def test_pdf_unlock(parser: PdfParser):
    password = parser.unlock_pdf(
        pdf_file_path="tests/integration/fixtures/protected.pdf",
        static_string="foobar",
        mask="?d?d?d",
    )

    assert password == "foobar123"


def test_override_password(hsbc: Hsbc):
    hsbc = Hsbc("tests/integration/fixtures/protected.pdf", password="foobar123")

    document = hsbc.open()
    assert not document.is_encrypted


def test_error_raised_if_override_is_wrong():
    with raises(ValueError, match="Wrong password"):
        hsbc = Hsbc("tests/integration/fixtures/protected.pdf", password="wrongpw")
        hsbc.open()
