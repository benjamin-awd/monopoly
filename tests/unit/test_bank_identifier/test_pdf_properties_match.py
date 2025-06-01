from monopoly.banks.detector import BankDetector
from monopoly.identifiers import MetadataIdentifier


def test_metadata_identifiers_match_partial(metadata_analyzer: BankDetector):
    metadata_identifier = MetadataIdentifier(format="PDF 1.6", creator="incorrect creator")
    metadata_analyzer.document.metadata_identifier = metadata_identifier

    bank_metadata_identifiers = [
        MetadataIdentifier(format="PDF 1.6", creator="correct creator"),
    ]

    assert not metadata_analyzer.metadata_identifiers_match(bank_metadata_identifiers)


def test_metadata_identifiers_match_wrong(metadata_analyzer: BankDetector):
    metadata_identifier = MetadataIdentifier(format="PDF 1.2", producer="foo")
    metadata_analyzer.metadata_identifier = metadata_identifier

    bank_metadata_identifiers = [MetadataIdentifier(format="PDF 1.6", producer="bar")]
    assert not metadata_analyzer.metadata_identifiers_match(bank_metadata_identifiers)


def test_metadata_identifiers_match_correct(metadata_analyzer: BankDetector):
    metadata_identifier = MetadataIdentifier(format="PDF 1.6", creator="correct creator")
    metadata_analyzer.metadata_identifier = metadata_identifier

    bank_metadata_identifiers = [
        MetadataIdentifier(format="PDF 1.6", creator="correct creator"),
    ]

    assert metadata_analyzer.metadata_identifiers_match(bank_metadata_identifiers)
