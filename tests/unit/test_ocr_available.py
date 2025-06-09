import pytest
from unittest.mock import Mock, PropertyMock

from monopoly.pdf import PdfParser
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class MockPdfDocument:
    def __init__(self, metadata: dict, raw_text: str):
        self.metadata_identifier = MetadataIdentifier(**metadata)
        self.raw_text = raw_text


@pytest.fixture
def mock_bank() -> Mock:
    return Mock()


def test_ocr_available_succeeds(mock_bank: Mock):
    mock_document = MockPdfDocument(
        metadata={"creator": "TestCreator", "producer": "TestProducer"}, raw_text="A document containing the MagicWord."
    )
    parser = PdfParser(bank=mock_bank, document=mock_document)

    bank_required_metadata = MetadataIdentifier(creator="TestCreator")
    bank_required_text = TextIdentifier(text="MagicWord")
    identifier_group = [[bank_required_metadata, bank_required_text]]

    type(mock_bank.pdf_config).ocr_identifiers = PropertyMock(return_value=identifier_group)

    assert parser.ocr_available == True


def test_ocr_available_succeeds_with_two_text_identifiers(mock_bank: Mock):
    """
    Tests that ocr_available returns True when a group with two
    TextIdentifiers fully matches the document.
    """
    mock_document = MockPdfDocument(
        metadata={"creator": "AnyCreator"}, raw_text="This document contains keyword_one and also keyword_two."
    )
    parser = PdfParser(bank=mock_bank, document=mock_document)

    bank_required_text_1 = TextIdentifier(text="keyword_one")
    bank_required_text_2 = TextIdentifier(text="keyword_two")
    identifier_group = [[bank_required_text_1, bank_required_text_2]]

    type(mock_bank.pdf_config).ocr_identifiers = PropertyMock(return_value=identifier_group)

    assert parser.ocr_available == True
