from unittest.mock import Mock, patch

import pytest

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.metadata import MetadataAnalyzer


@pytest.fixture
def mock_get_doc_byte_stream():
    with patch("monopoly.metadata.MetadataAnalyzer.get_doc_byte_stream") as mock:

        class MockBytes:
            def read(self, _):
                return b"%PDF-1.6"

        mock.return_value = MockBytes()
        yield mock


@pytest.fixture
def metadata_analyzer():
    return MetadataAnalyzer(None)


@pytest.mark.usefixtures("mock_get_doc_byte_stream")
def test_encryption_identifier(metadata_analyzer: MetadataAnalyzer):
    with patch("monopoly.metadata.MetadataAnalyzer.get_raw_encrypt_dict") as mock:
        mock.return_value = {"V": "4", "R": "4", "Length": "128", "P": "-1804"}

        metadata_analyzer.document = Mock()
        metadata_analyzer.document.metadata = None

        expected_identifier = EncryptionIdentifier(
            pdf_version=1.6, algorithm=4, revision=4, length=128, permissions=-1804
        )

        assert isinstance(metadata_analyzer.metadata_items[0], EncryptionIdentifier)
        assert metadata_analyzer.metadata_items[0] == expected_identifier


def test_metadata_identifier(
    mock_get_doc_byte_stream, metadata_analyzer: MetadataAnalyzer
):
    with patch("monopoly.metadata.MetadataAnalyzer.get_raw_encrypt_dict") as mock:
        mock.return_value = {}

        document_mock = Mock()
        document_mock.metadata = {
            "title": "foo",
            "author": "",
            "subject": "",
            "creator": "baz",
            "producer": "",
        }
        metadata_analyzer.document = document_mock
        metadata_analyzer.document.is_encrypted = False

        expected_identifier = MetadataIdentifier(
            title="foo",
            creator="baz",
        )

        assert isinstance(metadata_analyzer.metadata_items[0], MetadataIdentifier)
        assert metadata_analyzer.metadata_items[0] == expected_identifier
