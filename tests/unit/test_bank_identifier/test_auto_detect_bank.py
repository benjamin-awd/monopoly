from unittest.mock import PropertyMock, patch

import pytest

from monopoly.banks.base import BankBase
from monopoly.banks.detector import BankDetector
from monopoly.identifiers import MetadataIdentifier, TextIdentifier
from monopoly.pdf import PdfDocument


@pytest.fixture
def mock_encrypted_document():
    with patch(
        "monopoly.pdf.PdfParser.document", new_callable=PropertyMock
    ) as mock_document:
        mock_document_instance = mock_document.return_value
        type(mock_document_instance).metadata = PropertyMock(return_value={})
        yield mock_document


class MockBankOne(BankBase):
    statement_configs = None
    debit_config = None
    credit_config = None
    identifiers = [
        [
            MetadataIdentifier(creator="foo", producer="bar"),
        ]
    ]


class MockBankTwo(BankBase):
    statement_configs = None
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
    statement_configs = None
    debit_config = None
    credit_config = None
    identifiers = [[MetadataIdentifier(creator="asdasd", producer="qwerty")]]


class MockBankWithMultipleTextIdentifier(BankBase):
    statement_configs = None
    debit_config = None
    credit_config = None
    identifiers = [
        [
            MetadataIdentifier(creator="foo", producer="bar"),
            TextIdentifier("specific_string"),
            TextIdentifier("other_specific_string"),
        ]
    ]


class MockBankWithOnlyTextIdentifier(BankBase):
    statement_configs = None
    debit_config = None
    credit_config = None
    identifiers = [
        [
            TextIdentifier("foo"),
            TextIdentifier("baz"),
            TextIdentifier("bar"),
        ]
    ]


unencrypted_file_path = "path/to/unencrypted.pdf"
encrypted_file_path = "path/to/encrypted.pdf"


@patch.object(BankDetector, "metadata_items", new_callable=PropertyMock)
def test_auto_detect_bank_identified(
    mock_metadata_items, metadata_analyzer: BankDetector
):
    mock_metadata_items.return_value = [
        MetadataIdentifier(
            creator="Adobe Acrobat 23.3", producer="Adobe Acrobat Pro (64-bit)"
        )
    ]

    mock_banks_list = [MockBankOne, MockBankTwo]

    bank = metadata_analyzer.detect_bank(mock_banks_list)
    assert bank.__name__ == MockBankTwo.__name__


@patch.object(BankDetector, "metadata_items", new_callable=PropertyMock)
def test_detect_bank_not_identified(
    mock_metadata_items, metadata_analyzer: BankDetector
):
    mock_metadata_items.return_value = [
        MetadataIdentifier(creator="asdf", producer="qwerty")
    ]
    mock_banks_list = [MockBankThree]
    assert not metadata_analyzer.detect_bank(mock_banks_list)


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
@patch.object(BankDetector, "metadata_items", new_callable=PropertyMock)
def test_detect_bank_with_text_identifier(
    mock_metadata_items, mock_raw_text, metadata_analyzer: BankDetector
):
    mock_raw_text.return_value = "specific_string, other_specific_string"
    mock_metadata_items.return_value = [
        MetadataIdentifier(creator="foo", producer="bar"),
    ]

    mock_banks_list = [MockBankTwo, MockBankWithMultipleTextIdentifier]
    bank = metadata_analyzer.detect_bank(mock_banks_list)

    assert bank.__name__ == MockBankWithMultipleTextIdentifier.__name__


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
@patch.object(BankDetector, "metadata_items", new_callable=PropertyMock)
def test_detect_bank_with_not_matching_text_identifier(
    mock_metadata_items, mock_raw_text, monkeypatch, metadata_analyzer: BankDetector
):
    mock_raw_text.return_value = "not_a_match"
    mock_metadata_items.return_value = [
        MetadataIdentifier(creator="foo", producer="bar"),
    ]

    mock_banks_list = [MockBankTwo, MockBankWithMultipleTextIdentifier]
    monkeypatch.setattr("monopoly.banks.banks", mock_banks_list)

    assert not metadata_analyzer.detect_bank(mock_banks_list)


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
@patch.object(BankDetector, "metadata_items", new_callable=PropertyMock)
def test_detect_bank_with_only_text_identifier(
    mock_metadata_items, mock_raw_text, metadata_analyzer: BankDetector
):
    mock_raw_text.return_value = "foo baz bar"
    mock_metadata_items.return_value = [
        MetadataIdentifier(creator="foo", producer="bar")
    ]

    mock_banks_list = [
        MockBankWithMultipleTextIdentifier,
        MockBankWithOnlyTextIdentifier,
    ]

    bank = metadata_analyzer.detect_bank(mock_banks_list)
    assert bank.__name__ == MockBankWithOnlyTextIdentifier.__name__
