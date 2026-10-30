"""Detection and config selection for American Express, whose Singapore and US statements differ."""

from pathlib import Path
from unittest.mock import PropertyMock, patch

from test_utils.transactions import read_pages

from monopoly.banks import Amex
from monopoly.banks.detector import BankDetector
from monopoly.identifiers import MetadataIdentifier
from monopoly.pdf import PdfDocument, PdfPage

FIXTURES = Path(__file__).parents[2] / "integration" / "banks" / "amex"


def pages(statement: str) -> list[PdfPage]:
    return [PdfPage(text) for text in read_pages(FIXTURES / statement)]


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
def test_us_statement_detected(mock_raw_text, metadata_analyzer: BankDetector):
    mock_raw_text.return_value = "Website: americanexpress.com"
    metadata_analyzer.metadata_identifier = MetadataIdentifier(
        title="CSF.CRS.US.MTH.1A.ARC.D20260907.#00000001.PDF", creator="FIS Global Corp. - PDFSplit"
    )
    assert metadata_analyzer.detect_bank([Amex]) is Amex


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
def test_us_metadata_alone_is_not_amex(mock_raw_text, metadata_analyzer: BankDetector):
    # another issuer's statement from the same statement system
    mock_raw_text.return_value = "Website: example.com"
    metadata_analyzer.metadata_identifier = MetadataIdentifier(
        title="CSF.CRS.US.MTH.1A.ARC.D20260907.#00000001.PDF", creator="FIS Global Corp. - PDFSplit"
    )
    assert metadata_analyzer.detect_bank([Amex]) is None


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
def test_older_us_statement_detected(mock_raw_text, metadata_analyzer: BankDetector):
    # statements from before 2024, as the online archive renders them
    mock_raw_text.return_value = "Account Ending 9-12345\nWebsite: americanexpress.com"
    metadata_analyzer.metadata_identifier = MetadataIdentifier(title="PRO Document", creator="PRO HLCAPI")
    assert metadata_analyzer.detect_bank([Amex]) is Amex


@patch.object(PdfDocument, "raw_text", new_callable=PropertyMock)
def test_older_metadata_needs_a_us_account(mock_raw_text, metadata_analyzer: BankDetector):
    # the same document system with no US account line
    mock_raw_text.return_value = "Website: americanexpress.com"
    metadata_analyzer.metadata_identifier = MetadataIdentifier(title="PRO Document", creator="PRO HLCAPI")
    assert metadata_analyzer.detect_bank([Amex]) is None


def test_each_config_reads_only_its_own_statements():
    assert Amex.us.find_header(pages("us")) is not None
    assert Amex.us.find_header(pages("us_older")) is not None
    assert Amex.platinum.find_header(pages("us_older")) is None
    assert Amex.platinum.find_header(pages("us")) is None
    assert Amex.us.find_header(pages("credit")) is None
