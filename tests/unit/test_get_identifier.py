from unittest.mock import Mock

from monopoly.banks.base import BankBase
from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.pdf import PdfParser


class TestGetIdentifier:
    def test_encryption_identifier(parser: PdfParser):
        extractor_mock = Mock()
        extractor_mock.pdf._header_version = (1, 6)
        extractor_mock.algorithm = 4
        extractor_mock.length = 128
        extractor_mock.permissions = -1804
        extractor_mock.revision = 4

        parser.extractor = extractor_mock

        identifier = BankBase.get_identifier(parser)

        expected_identifier = EncryptionIdentifier(
            pdf_version=1.6, algorithm=4, revision=4, length=128, permissions=-1804
        )

        assert isinstance(identifier, EncryptionIdentifier)
        assert identifier == expected_identifier

    def test_metadata_identifier(parser):
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
        identifier = BankBase.get_identifier(parser)

        expected_identifier = MetadataIdentifier(
            title="foo",
            creator="baz",
        )

        assert isinstance(identifier, MetadataIdentifier)
        assert identifier == expected_identifier
