from io import BytesIO
from unittest.mock import Mock, patch

import pytest

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.metadata import MetadataAnalyzer
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
        self.metadata = metadata

    def open(self):
        return MockDocument(self.is_encrypted, self.metadata)

    def get_byte_stream(self):
        return BytesIO(b"%PDF-1.6")


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


def test_encryption_identifier(mock_encrypted_document):
    with patch("monopoly.metadata.MetadataAnalyzer.get_raw_encrypt_dict") as mock:
        metadata_analyzer = MetadataAnalyzer(mock_encrypted_document)
        mock.return_value = {"V": "4", "R": "4", "Length": "128", "P": "-1804"}

        expected_identifier = EncryptionIdentifier(
            pdf_version=1.6, algorithm=4, revision=4, length=128, permissions=-1804
        )

        assert isinstance(metadata_analyzer.metadata_items[0], EncryptionIdentifier)
        assert metadata_analyzer.metadata_items[0] == expected_identifier


def test_metadata_identifier(mock_non_encrypted_document):
    with patch.object(PdfDocument, "open", new_callable=Mock) as mock_open:
        mock_open.return_value = mock_non_encrypted_document

        expected_identifier = MetadataIdentifier(
            title="foo",
            creator="baz",
        )

        metadata_analyzer = MetadataAnalyzer(mock_non_encrypted_document)

        assert isinstance(metadata_analyzer.metadata_items[0], MetadataIdentifier)
        assert metadata_analyzer.metadata_items[0] == expected_identifier
