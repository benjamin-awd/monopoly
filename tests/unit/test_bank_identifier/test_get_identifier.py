from unittest.mock import Mock, patch

import pytest

from monopoly.banks.detector import BankDetector
from monopoly.identifiers import MetadataIdentifier
from monopoly.pdf import PdfDocument


class MockDocument:
    def __init__(self, is_encrypted, metadata):
        self.is_encrypted = is_encrypted
        self.metadata = metadata

    def xref_get_key(self):
        return None


class MockPdfDocument:
    def __init__(self, is_encrypted: bool, metadata: dict):
        self.is_encrypted = is_encrypted
        self.metadata_identifier = MetadataIdentifier(**metadata)

    def open(self):
        return MockDocument(self.is_encrypted, self.metadata_identifier)


@pytest.fixture
def mock_encrypted_document():
    yield MockPdfDocument(
        is_encrypted=True,
        metadata={
            "title": "foo",
            "author": "",
            "subject": "",
            "creator": "baz",
            "producer": "",
        },
    )


@pytest.fixture
def mock_non_encrypted_document():
    yield MockPdfDocument(
        is_encrypted=False,
        metadata={
            "title": "foo",
            "author": "",
            "subject": "",
            "creator": "baz",
            "producer": "",
        },
    )


def test_metadata_identifier(mock_non_encrypted_document):
    with patch.object(PdfDocument, "unlock_document", new_callable=Mock) as mock_unlock:
        mock_unlock.return_value = mock_non_encrypted_document

        expected_identifier = MetadataIdentifier(
            title="foo",
            creator="baz",
        )

        metadata_analyzer = BankDetector(mock_non_encrypted_document)

        assert isinstance(metadata_analyzer.metadata_identifier, MetadataIdentifier)
        assert metadata_analyzer.metadata_identifier == expected_identifier
