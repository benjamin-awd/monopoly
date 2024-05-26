from unittest.mock import Mock, patch

import pytest

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.pdf import PdfParser


@pytest.fixture
def mock_get_doc_byte_stream():
    with patch("monopoly.pdf.PdfParser._get_doc_byte_stream") as mock:

        class MockBytes:
            def read(self, _):
                return b"%PDF-1.6"

        mock.return_value = MockBytes()
        yield mock


def test_encryption_identifier(mock_get_doc_byte_stream, parser: PdfParser):
    with patch("monopoly.pdf.PdfParser._get_raw_encrypt_dict") as mock:
        mock.return_value = {"V": "4", "R": "4", "Length": "128", "P": "-1804"}

        parser.document = Mock()
        parser.document.metadata = None

        expected_identifier = EncryptionIdentifier(
            pdf_version=1.6, algorithm=4, revision=4, length=128, permissions=-1804
        )

        assert isinstance(parser.metadata_items[0], EncryptionIdentifier)
        assert parser.metadata_items[0] == expected_identifier


def test_metadata_identifier(mock_get_doc_byte_stream, parser: PdfParser):
    with patch("monopoly.pdf.PdfParser._get_raw_encrypt_dict") as mock:
        mock.return_value = {}

        document_mock = Mock()
        document_mock.metadata = {
            "title": "foo",
            "author": "",
            "subject": "",
            "creator": "baz",
            "producer": "",
        }
        parser.document = document_mock
        parser.document.is_encrypted = False

        expected_identifier = MetadataIdentifier(
            title="foo",
            creator="baz",
        )

        assert isinstance(parser.metadata_items[0], MetadataIdentifier)
        assert parser.metadata_items[0] == expected_identifier
