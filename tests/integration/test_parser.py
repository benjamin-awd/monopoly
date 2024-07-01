from pathlib import Path
from typing import Type

import pytest
from pydantic import SecretStr
from pytest import raises

from monopoly.banks import BankBase
from monopoly.config import PdfConfig
from monopoly.pdf import (
    BadPasswordFormatError,
    MissingPasswordError,
    PdfParser,
    WrongPasswordError,
)

fixture_directory = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="function")
def mock_bank():
    class MockBank:
        pdf_config = PdfConfig()
        passwords = None

    return MockBank()


def test_can_open_file_stream(parser: PdfParser):
    with open(fixture_directory / "4_pages_blank.pdf", "rb") as file:
        parser.file_bytes = file.read()
        document = parser.open()
        assert len(document) == 4


def test_can_open_protected(parser: PdfParser):
    parser.file_path = fixture_directory / "protected.pdf"

    parser.open([SecretStr("foobar123")])


def test_wrong_password_raises_error(parser: PdfParser):
    parser.file_path = fixture_directory / "protected.pdf"

    with raises(WrongPasswordError, match="Could not open"):
        parser.open([SecretStr("wrong_pw")])


def test_get_pages(parser: PdfParser, mock_bank: Type[BankBase]):
    parser.file_path = fixture_directory / "4_pages_blank.pdf"
    mock_bank.pdf_config.page_range = (0, -1)

    pages = parser.get_pages(mock_bank)
    assert len(pages) == 3


def test_get_pages_invalid_returns_error(parser: PdfParser, mock_bank: Type[BankBase]):
    parser.file_path = fixture_directory / "4_pages_blank.pdf"
    mock_bank.pdf_config.page_range = (99, -99)

    with raises(ValueError, match="bad page number"):
        parser.get_pages(mock_bank)


def test_override_password(parser: PdfParser):
    parser.file_path = fixture_directory / "protected.pdf"
    document = parser.open([SecretStr("foobar123")])
    assert not document.is_encrypted


def test_error_raised_if_override_is_wrong(parser: PdfParser):
    with raises(WrongPasswordError, match="Could not open"):
        parser.file_path = fixture_directory / "protected.pdf"
        parser.open([SecretStr("wrongpw")])


def test_missing_password_raises_error(parser: PdfParser):
    parser.file_path = fixture_directory / "protected.pdf"

    with raises(MissingPasswordError, match="No password found in PDF configuration"):
        parser.open()


def test_null_password_raises_error(parser: PdfParser):
    parser.file_path = fixture_directory / "protected.pdf"

    with raises(MissingPasswordError, match="is empty"):
        parser.open([SecretStr("")])


def test_invalid_password_type_raises_error(parser: PdfParser):
    parser.file_path = fixture_directory / "protected.pdf"

    with raises(BadPasswordFormatError, match="should be stored in a list"):
        parser.open("not a list")


def test_plain_text_passwords_raises_error(parser: PdfParser):
    parser.file_path = fixture_directory / "protected.pdf"

    with raises(BadPasswordFormatError, match="should be stored as SecretStr"):
        parser.open(["password"])
