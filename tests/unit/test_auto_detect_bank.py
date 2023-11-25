from unittest.mock import PropertyMock, patch

import pytest
from pytest import raises
from test_utils.skip import skip_if_encrypted

from monopoly.banks import auto_detect_bank
from monopoly.banks.base import BankBase
from monopoly.constants import EncryptionIdentifier, MetadataIdentifier


@pytest.fixture
def mock_pdf_parser():
    with patch(
        "monopoly.pdf.PdfParser.document", new_callable=PropertyMock
    ) as mock_document:
        mock_document_instance = mock_document.return_value
        # Set the metadata attribute to the desired value
        type(mock_document_instance).metadata = PropertyMock(
            return_value={
                "creator": "Adobe Acrobat 23.3",
                "producer": "Adobe Acrobat Pro (64-bit)",
            }
        )

        with patch("monopoly.pdf.PdfParser") as mock_parser:
            mock_instance = mock_parser.return_value
            type(mock_instance).document = PropertyMock(
                return_value=mock_document_instance
            )
            yield mock_parser


@pytest.fixture
def mock_pdf_hash_extractor():
    with patch("monopoly.pdf.PdfHashExtractor") as mock_extractor:
        # Customize the mock behavior if needed
        mock_instance = mock_extractor.return_value
        mock_instance.pdf._header_version = (1, 0)
        yield mock_extractor


class MockBankOne(BankBase):
    statement_config = None
    transaction_config = None
    identifiers = [
        EncryptionIdentifier(
            pdf_version=1.7, algorithm=5, revision=6, length=256, permissions=-1028
        ),
        MetadataIdentifier(creator="foo", producer="bar"),
    ]


class MockBankTwo(BankBase):
    statement_config = None
    transaction_config = None
    identifiers = [
        MetadataIdentifier(
            creator="Adobe Acrobat 23.3", producer="Adobe Acrobat Pro (64-bit)"
        )
    ]


unencrypted_file_path = "tests/integration/banks/example/input.pdf"
encrypted_file_path = "tests/integration/fixtures/protected.pdf"


@skip_if_encrypted
def test_auto_detect_unencrypted_bank_identified(
    monkeypatch,
    mock_pdf_parser,
    mock_pdf_hash_extractor,
    file_path: str = unencrypted_file_path,
):
    mock_banks_list = [MockBankOne, MockBankTwo]
    monkeypatch.setattr("monopoly.banks.banks", mock_banks_list)
    bank_instance = auto_detect_bank(
        file_path=file_path,
    )
    assert isinstance(bank_instance, MockBankTwo)


def test_auto_detect_encrypted_bank_identified(
    monkeypatch, file_path: str = encrypted_file_path
):
    mock_banks_list = [MockBankOne, MockBankTwo]
    monkeypatch.setattr("monopoly.banks.banks", mock_banks_list)
    bank_instance = auto_detect_bank(
        file_path=file_path,
    )
    assert isinstance(bank_instance, MockBankOne)


@skip_if_encrypted
def test_auto_detect_bank_not_identified(
    monkeypatch,
    mock_pdf_parser,
    mock_pdf_hash_extractor,
    file_path: str = unencrypted_file_path,
):
    mock_banks_list = [MockBankOne]
    monkeypatch.setattr("monopoly.banks.banks", mock_banks_list)

    with raises(ValueError, match=f"Could not find a bank for {file_path}"):
        auto_detect_bank(file_path=file_path)
