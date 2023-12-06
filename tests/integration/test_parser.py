from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest import raises

from monopoly.pdf import PdfParser
from monopoly.processors import Hsbc

fixture_directory = Path(__file__).parent / "fixtures"


def test_can_open_protected(parser: PdfParser):
    parser.file_path = fixture_directory / "protected.pdf"
    parser.passwords = ["foobar123"]

    parser.open()


def test_wrong_password_raises_error(parser: PdfParser):
    parser.file_path = fixture_directory / "protected.pdf"
    parser.passwords = ["wrong_pw"]

    with raises(ValueError, match="Wrong password"):
        parser.open()


def test_get_pages(parser: PdfParser):
    parser.file_path = fixture_directory / "4_pages_blank.pdf"
    parser.page_range = slice(0, -1)

    pages = parser.get_pages()
    assert len(pages) == 3


def test_get_pages_invalid_returns_error(parser: PdfParser):
    parser.file_path = fixture_directory / "4_pages_blank.pdf"
    parser.page_range = slice(99, -99)

    with raises(ValueError, match="bad page number"):
        parser.get_pages()


def test_override_password(hsbc: Hsbc):
    with patch.object(PdfParser, "get_pages") as mock_get_pages:
        mock_get_pages.return_value = MagicMock()
        hsbc = Hsbc(fixture_directory / "protected.pdf", passwords=["foobar123"])
        document = hsbc.parser.open()
        assert not document.is_encrypted


def test_error_raised_if_override_is_wrong():
    with raises(ValueError, match="Wrong password"):
        hsbc = Hsbc(fixture_directory / "protected.pdf", passwords=["wrongpw"])
        hsbc.open()
