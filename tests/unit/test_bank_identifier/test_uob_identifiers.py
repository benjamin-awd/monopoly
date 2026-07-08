"""Detection tests for UOB, which renders account and card statements differently."""

from unittest.mock import PropertyMock, patch

from monopoly.banks import Uob
from monopoly.banks.detector import BankDetector
from monopoly.identifiers import MetadataIdentifier
from monopoly.pdf import PdfDocument


def test_uob_detected_regardless_of_pdf_version(metadata_analyzer: BankDetector):
    # Account (debit) statements are rendered as PDF 1.4, credit card
    # statements as PDF 1.5 - detection must not depend on the version.
    metadata_analyzer.metadata_identifier = MetadataIdentifier(
        format="PDF 1.4",
        creator="Vault Rendering Engine",
        producer="Rendering Engine 7.4.1.9",
    )
    assert metadata_analyzer.detect_bank([Uob]) is Uob


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
def test_uob_detected_via_customer_service_text(mock_raw_text, metadata_analyzer: BankDetector):
    # Fall back to the account-statement contact email when metadata differs.
    mock_raw_text.return_value = "Email customer.service@uobgroup.com"
    metadata_analyzer.metadata_identifier = MetadataIdentifier(creator="unknown", producer="unknown")
    assert metadata_analyzer.detect_bank([Uob]) is Uob
