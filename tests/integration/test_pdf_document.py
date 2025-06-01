from pathlib import Path
from unittest.mock import MagicMock, patch

from pydantic import SecretStr
from pytest import raises

from monopoly.pdf import (
    BadPasswordFormatError,
    MissingPasswordError,
    PdfDocument,
    WrongPasswordError,
)

fixture_directory = Path(__file__).parent / "fixtures"


def test_document_initialization_with_both_raises_error():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    with raises(RuntimeError, match="Only one of `file_path` or `file_bytes` should be passed"):
        PdfDocument(file_path=file_path, file_bytes=b"123")


def test_document_initialization_with_neither_raises_error():
    with raises(RuntimeError, match="Either `file_path` or `file_bytes` must be passed"):
        PdfDocument()


def test_can_open_file_stream():
    with open(fixture_directory / "4_pages_blank.pdf", "rb") as file:
        pdf_document = PdfDocument(file_bytes=file.read())
        assert len(pdf_document) == 4


def test_can_open_protected(pdf_document: PdfDocument):
    mock_pdf_passwords_instance = MagicMock()
    mock_pdf_passwords_instance.pdf_passwords = [SecretStr("foobar123")]

    with patch("monopoly.pdf.PdfPasswords", return_value=mock_pdf_passwords_instance):
        pdf_document = PdfDocument(passwords=None, file_path=fixture_directory / "protected.pdf")
        pdf_document.unlock_document()


def test_wrong_password_raises_error():
    with raises(WrongPasswordError, match="Could not open"):
        pdf_document: PdfDocument = PdfDocument(
            passwords=[SecretStr("wrongpw_123")],
            file_path=fixture_directory / "protected.pdf",
        )
        pdf_document.unlock_document()


def test_override_password():
    pdf_document: PdfDocument = PdfDocument(
        passwords=[SecretStr("foobar123")],
        file_path=fixture_directory / "protected.pdf",
    )
    pdf_document.unlock_document()
    assert not pdf_document.is_encrypted


def test_missing_password_raises_error():
    mock_pdf_passwords_instance = MagicMock()
    mock_pdf_passwords_instance.pdf_passwords = []

    with raises(MissingPasswordError):
        with patch("monopoly.pdf.PdfPasswords", return_value=mock_pdf_passwords_instance):
            pdf_document = PdfDocument(passwords=None, file_path=fixture_directory / "protected.pdf")
            pdf_document.unlock_document()


def test_null_password_raises_error():
    mock_pdf_passwords_instance = MagicMock()
    mock_pdf_passwords_instance.pdf_passwords = [SecretStr("")]

    with raises(MissingPasswordError, match="is empty"):
        with patch("monopoly.pdf.PdfPasswords", return_value=mock_pdf_passwords_instance):
            pdf_document = PdfDocument(passwords=None, file_path=fixture_directory / "protected.pdf")
            pdf_document.unlock_document()


def test_invalid_password_type_raises_error():
    mock_pdf_passwords_instance = MagicMock()
    mock_pdf_passwords_instance.pdf_passwords = "not a list"

    with raises(BadPasswordFormatError, match="should be stored in a list"):
        with patch("monopoly.pdf.PdfPasswords", return_value=mock_pdf_passwords_instance):
            pdf_document = PdfDocument(passwords=None, file_path=fixture_directory / "protected.pdf")
            pdf_document.unlock_document()


def test_plain_text_passwords_raises_error(pdf_document: PdfDocument):
    mock_pdf_passwords_instance = MagicMock()
    mock_pdf_passwords_instance.pdf_passwords = ["insecure"]

    with raises(BadPasswordFormatError, match="should be stored as SecretStr"):
        with patch("monopoly.pdf.PdfPasswords", return_value=mock_pdf_passwords_instance):
            pdf_document = PdfDocument(passwords=None, file_path=fixture_directory / "protected.pdf")
            pdf_document.unlock_document()
