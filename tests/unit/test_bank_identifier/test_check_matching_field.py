from unittest.mock import Mock

from monopoly.bank_detector import BankDetector
from monopoly.identifiers import EncryptionIdentifier, MetadataIdentifier


def test_check_metadata_identifier_field_exact_match(
    metadata_analyzer: BankDetector,
):
    field = Mock()
    field.name = "title"
    field.type = str
    metadata = MetadataIdentifier(title="statement")
    identifier = MetadataIdentifier(title="statement")

    assert metadata_analyzer.check_matching_field(field, metadata, identifier)


def test_check_encryption_identifier_field_exact_match(
    metadata_analyzer: BankDetector,
):
    field = Mock()
    field.name = "pdf_version"
    field.type = float
    metadata = EncryptionIdentifier(
        pdf_version=9.0, algorithm=1, revision=2, length=3, permissions=4
    )
    identifier = EncryptionIdentifier(
        pdf_version=9.0, algorithm=1, revision=2, length=3, permissions=4
    )

    assert metadata_analyzer.check_matching_field(field, metadata, identifier)


def test_check_matching_field_partial_string_match(metadata_analyzer: BankDetector):
    field = Mock()
    field.name = "creator"
    field.type = str
    metadata = MetadataIdentifier(creator="extremely long creator name version 12345")
    identifier = MetadataIdentifier(creator="extremely long creator")

    assert metadata_analyzer.check_matching_field(field, metadata, identifier)


def test_check_matching_field_no_match(metadata_analyzer: BankDetector):
    field = Mock()
    field.name = "author"
    field.type = str
    metadata = MetadataIdentifier(author="robin")
    identifier = MetadataIdentifier(author="hood")

    assert not metadata_analyzer.check_matching_field(field, metadata, identifier)
