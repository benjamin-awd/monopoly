from unittest.mock import PropertyMock, patch

import pytest
from test_utils.skip import skip_if_encrypted

from monopoly.banks import detect_bank
from monopoly.banks.base import BankBase
from monopoly.constants import EncryptionIdentifier, MetadataIdentifier


@pytest.fixture
def mock_encrypt_metadata_extractor():
    with patch("monopoly.pdf.EncryptionMetadataExtractor") as mock_extractor:
        mock_instance = mock_extractor.return_value
        mock_instance.pdf._header_version = (1, 7)
        mock_instance.revision = 6
        mock_instance.length = 256
        mock_instance.permissions = -1028
        mock_instance.algorithm = 5
        yield mock_extractor


@pytest.fixture
def mock_no_encrypt_metadata_extractor():
    with patch("monopoly.pdf.EncryptionMetadataExtractor") as mock_extractor:
        mock_instance = mock_extractor.return_value
        mock_instance.pdf._header_version = (1, 7)
        yield mock_extractor


@pytest.fixture
def mock_encrypted_document():
    with patch(
        "monopoly.pdf.PdfParser.document", new_callable=PropertyMock
    ) as mock_document:
        mock_document_instance = mock_document.return_value
        # Set the metadata attribute to the desired value
        type(mock_document_instance).metadata = PropertyMock(return_value={})
        yield mock_document


class MockBankOne(BankBase):
    debit_config = None
    credit_config = None
    identifiers = [
        EncryptionIdentifier(
            pdf_version=1.7, algorithm=5, revision=6, length=256, permissions=-1028
        ),
        MetadataIdentifier(creator="foo", producer="bar"),
    ]


class MockBankTwo(BankBase):
    debit_config = None
    credit_config = None
    identifiers = [
        MetadataIdentifier(
            creator="Adobe Acrobat 23.3", producer="Adobe Acrobat Pro (64-bit)"
        )
    ]


class MockBankThree(BankBase):
    debit_config = None
    credit_config = None
    identifiers = [MetadataIdentifier(creator="asdasd", producer="qwerty")]


unencrypted_file_path = "path/to/unencrypted.pdf"
encrypted_file_path = "path/to/encrypted.pdf"


@skip_if_encrypted
def test_auto_detectbank_identified(
    monkeypatch,
):
    identifiers = MockBankTwo.identifiers
    mock_banks_list = [MockBankOne, MockBankTwo]
    monkeypatch.setattr("monopoly.banks.banks", mock_banks_list)

    bank = detect_bank(identifiers, "")

    assert bank.__name__ == MockBankTwo.__name__


@skip_if_encrypted
def test_detect_bank_not_identified(
    monkeypatch,
):
    mock_banks_list = [MockBankThree]
    monkeypatch.setattr("monopoly.banks.banks", mock_banks_list)

    # None should be returned here
    assert not detect_bank([MetadataIdentifier(creator="asdf", producer="qwerty")], "")
