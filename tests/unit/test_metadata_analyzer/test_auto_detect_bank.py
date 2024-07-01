from unittest.mock import PropertyMock, patch

import pytest
from test_utils.skip import skip_if_encrypted

from monopoly.banks.base import BankBase
from monopoly.constants import EncryptionIdentifier, MetadataIdentifier, TextIdentifier
from monopoly.metadata import MetadataAnalyzer


@pytest.fixture
def mock_encrypted_document():
    with patch(
        "monopoly.pdf.PdfParser.document", new_callable=PropertyMock
    ) as mock_document:
        mock_document_instance = mock_document.return_value
        type(mock_document_instance).metadata = PropertyMock(return_value={})
        yield mock_document


class MockBankOne(BankBase):
    debit_config = None
    credit_config = None
    identifiers = [
        [
            EncryptionIdentifier(
                pdf_version=1.7, algorithm=5, revision=6, length=256, permissions=-1028
            ),
            MetadataIdentifier(creator="foo", producer="bar"),
        ]
    ]


class MockBankTwo(BankBase):
    debit_config = None
    credit_config = None
    identifiers = [
        [
            MetadataIdentifier(
                creator="Adobe Acrobat 23.3", producer="Adobe Acrobat Pro (64-bit)"
            )
        ]
    ]


class MockBankThree(BankBase):
    debit_config = None
    credit_config = None
    identifiers = [[MetadataIdentifier(creator="asdasd", producer="qwerty")]]


class MockBankWithMultipleTextIdentifier(BankBase):
    debit_config = None
    credit_config = None
    identifiers = [
        [
            EncryptionIdentifier(
                pdf_version=1.7, algorithm=5, revision=6, length=256, permissions=-1028
            ),
            MetadataIdentifier(creator="foo", producer="bar"),
            TextIdentifier("specific_string"),
            TextIdentifier("other_specific_string"),
        ]
    ]


unencrypted_file_path = "path/to/unencrypted.pdf"
encrypted_file_path = "path/to/encrypted.pdf"


@skip_if_encrypted
@patch.object(MetadataAnalyzer, "metadata_items", new_callable=PropertyMock)
def test_auto_detect_bank_identified(
    mock_metadata_items, monkeypatch, metadata_analyzer: MetadataAnalyzer
):
    mock_metadata_items.return_value = [
        MetadataIdentifier(
            creator="Adobe Acrobat 23.3", producer="Adobe Acrobat Pro (64-bit)"
        )
    ]

    mock_banks_list = [MockBankOne, MockBankTwo]
    monkeypatch.setattr("monopoly.metadata.banks", mock_banks_list)

    bank = metadata_analyzer.detect_bank()

    assert bank.__name__ == MockBankTwo.__name__


@skip_if_encrypted
@patch.object(MetadataAnalyzer, "metadata_items", new_callable=PropertyMock)
def test_detect_bank_not_identified(
    mock_metadata_items, monkeypatch, metadata_analyzer: MetadataAnalyzer
):
    mock_metadata_items.return_value = [
        MetadataIdentifier(creator="asdf", producer="qwerty")
    ]
    mock_banks_list = [MockBankThree]
    monkeypatch.setattr("monopoly.metadata.banks", mock_banks_list)

    # None should be returned here
    assert not metadata_analyzer.detect_bank()


@skip_if_encrypted
@patch.object(MetadataAnalyzer, "raw_text", new_callable=PropertyMock)
@patch.object(MetadataAnalyzer, "metadata_items", new_callable=PropertyMock)
def test_detect_bank_with_text_identifier(
    mock_metadata_items, mock_raw_text, monkeypatch, metadata_analyzer: MetadataAnalyzer
):
    mock_raw_text.return_value = "specific_string, other_specific_string"
    mock_metadata_items.return_value = [
        EncryptionIdentifier(
            pdf_version=1.7, algorithm=5, revision=6, length=256, permissions=-1028
        ),
        MetadataIdentifier(creator="foo", producer="bar"),
    ]

    mock_banks_list = [MockBankTwo, MockBankWithMultipleTextIdentifier]
    monkeypatch.setattr("monopoly.metadata.banks", mock_banks_list)

    bank = metadata_analyzer.detect_bank()

    assert bank.__name__ == MockBankWithMultipleTextIdentifier.__name__


@skip_if_encrypted
@patch.object(MetadataAnalyzer, "raw_text", new_callable=PropertyMock)
@patch.object(MetadataAnalyzer, "metadata_items", new_callable=PropertyMock)
def test_detect_bank_with_not_matching_text_identifier(
    mock_metadata_items, mock_raw_text, monkeypatch, metadata_analyzer: MetadataAnalyzer
):
    mock_raw_text.return_value = "not_a_match"
    mock_metadata_items.return_value = [
        EncryptionIdentifier(
            pdf_version=1.7, algorithm=5, revision=6, length=256, permissions=-1028
        ),
        MetadataIdentifier(creator="foo", producer="bar"),
    ]

    mock_banks_list = [MockBankTwo, MockBankWithMultipleTextIdentifier]
    monkeypatch.setattr("monopoly.metadata.banks", mock_banks_list)

    assert not metadata_analyzer.detect_bank()
