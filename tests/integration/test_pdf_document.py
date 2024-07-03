from pathlib import Path
from unittest.mock import PropertyMock, patch

from pydantic import SecretStr
from pytest import raises

from monopoly.pdf import (
    BadPasswordFormatError,
    MissingPasswordError,
    PdfDocument,
    WrongPasswordError,
)

fixture_directory = Path(__file__).parent / "fixtures"


def test_can_open_file_stream(pdf_document: PdfDocument):
    with open(fixture_directory / "4_pages_blank.pdf", "rb") as file:
        pdf_document.file_bytes = file.read()
        document = pdf_document.open()
        assert len(document) == 4


def test_can_open_protected(pdf_document: PdfDocument):
    pdf_document.file_path = fixture_directory / "protected.pdf"
    pdf_document._passwords = [SecretStr("foobar123")]

    pdf_document.open()


def test_wrong_password_raises_error(pdf_document: PdfDocument):
    pdf_document.file_path = fixture_directory / "protected.pdf"
    pdf_document._passwords = [SecretStr("wrong_pw")]

    with raises(WrongPasswordError, match="Could not open"):
        pdf_document.open()


def test_override_password(pdf_document: PdfDocument):
    pdf_document.file_path = fixture_directory / "protected.pdf"
    pdf_document._passwords = [SecretStr("foobar123")]
    pdf_document = pdf_document.open()
    assert not pdf_document.is_encrypted


def test_error_raised_if_override_is_wrong(pdf_document: PdfDocument):
    with raises(WrongPasswordError, match="Could not open"):
        pdf_document.file_path = fixture_directory / "protected.pdf"
        pdf_document._passwords = [SecretStr("wrongpw")]
        pdf_document.open()


def test_missing_password_raises_error(pdf_document: PdfDocument):
    pdf_document.file_path = fixture_directory / "protected.pdf"
    with patch(
        "monopoly.pdf.PdfDocument.passwords", new_callable=PropertyMock
    ) as mock_passwords:
        mock_passwords.return_value = None
        with raises(
            MissingPasswordError, match="No password found in PDF configuration"
        ):
            pdf_document.open()


def test_null_password_raises_error(pdf_document: PdfDocument):
    pdf_document.file_path = fixture_directory / "protected.pdf"
    pdf_document._passwords = [SecretStr("")]

    with raises(MissingPasswordError, match="is empty"):
        pdf_document.open()


def test_invalid_password_type_raises_error(pdf_document: PdfDocument):
    pdf_document.file_path = fixture_directory / "protected.pdf"
    pdf_document._passwords = "not a list"

    with raises(BadPasswordFormatError, match="should be stored in a list"):
        pdf_document.open()


def test_plain_text_passwords_raises_error(pdf_document: PdfDocument):
    pdf_document.file_path = fixture_directory / "protected.pdf"
    pdf_document._passwords = ["password"]

    with raises(BadPasswordFormatError, match="should be stored as SecretStr"):
        pdf_document.open()
