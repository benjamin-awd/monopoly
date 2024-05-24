from unittest.mock import Mock

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.pdf import PdfParser


def test_encryption_identifier(parser: PdfParser):
    parser.extractor = Mock()
    parser.extractor.pdf._header_version = (1, 6)
    parser.extractor.algorithm = 4
    parser.extractor.length = 128
    parser.extractor.permissions = -1804
    parser.extractor.revision = 4

    parser.document = Mock()
    parser.document.metadata = None

    expected_identifier = EncryptionIdentifier(
        pdf_version=1.6, algorithm=4, revision=4, length=128, permissions=-1804
    )

    assert isinstance(parser.metadata_items[0], EncryptionIdentifier)
    assert parser.metadata_items[0] == expected_identifier


def test_metadata_identifier(parser: PdfParser):
    document_mock = Mock()
    document_mock.metadata = {
        "title": "foo",
        "author": "",
        "subject": "",
        "creator": "baz",
        "producer": "",
    }
    parser.extractor = Mock()
    parser.extractor.encrypt_dict = None
    parser.document = document_mock

    expected_identifier = MetadataIdentifier(
        title="foo",
        creator="baz",
    )

    assert isinstance(parser.metadata_items[0], MetadataIdentifier)
    assert parser.metadata_items[0] == expected_identifier
