"""Detection tests for DBS, whose statements were rendered by different engines over the years."""

from unittest.mock import PropertyMock, patch

from monopoly.banks import Dbs
from monopoly.banks.detector import BankDetector
from monopoly.identifiers import MetadataIdentifier
from monopoly.pdf import PdfDocument


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
def test_dbs_detected_for_quadient_statements(mock_raw_text, metadata_analyzer: BankDetector):
    mock_raw_text.return_value = "DBS Cards P.O. Box"
    metadata_analyzer.metadata_identifier = MetadataIdentifier(format="PDF 1.4", creator="Quadient CXM AG~Inspire~15.0")
    assert metadata_analyzer.detect_bank([Dbs]) is Dbs


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
def test_dbs_detected_for_legacy_streamserve_statements(mock_raw_text, metadata_analyzer: BankDetector):
    # Statements issued before mid-2021: creator "DBS", rendered by StreamServe, titled "OnDemand Copy"
    mock_raw_text.return_value = "DBS Cards P.O. Box"
    metadata_analyzer.metadata_identifier = MetadataIdentifier(
        format="PDF 1.4",
        title="OnDemand Copy",
        author="DBS",
        creator="DBS",
        producer="StreamServe Communication Server 5.6.2 GA Build 374 (64 bit)",
    )
    assert metadata_analyzer.detect_bank([Dbs]) is Dbs


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
def test_streamserve_alone_is_not_dbs(mock_raw_text, metadata_analyzer: BankDetector):
    # StreamServe renders statements for other issuers too: the creator and the text must both say DBS
    mock_raw_text.return_value = "Some Other Bank"
    metadata_analyzer.metadata_identifier = MetadataIdentifier(creator="Other", producer="StreamServe Communication Server")
    assert metadata_analyzer.detect_bank([Dbs]) is None
