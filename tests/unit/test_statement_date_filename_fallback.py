"""Test filename fallback for statement dates when not found in content."""

from datetime import datetime
from pathlib import Path

from monopoly.banks import Citibank
from monopoly.pdf import PdfPage
from monopoly.statements import CreditStatement


def test_filename_fallback_nov2025():
    """Test that statement date can be extracted from filename: eStatement_Nov2025_*.pdf"""
    # Create a statement with pages that don't contain the statement date pattern
    pages = [PdfPage(raw_text="DATE  DESCRIPTION  AMOUNT\n15 Nov  TEST TRANSACTION  100.00")]

    file_path = Path("/tmp/eStatement_Nov2025_2025-11-07T14_50_26.pdf")
    statement = CreditStatement(
        pages=pages,
        bank_name="Citibank",
        config=Citibank.credit,
        header="date description amount",
        file_path=file_path,
    )

    result_date = statement.statement_date
    assert result_date.year == 2025
    assert result_date.month == 11
    assert result_date.day == 1  # Fallback sets day to 1


def test_filename_fallback_oct2025():
    """Test that statement date can be extracted from filename: CardStatement_Oct2025.pdf"""
    pages = [PdfPage(raw_text="DATE  DESCRIPTION  AMOUNT\n15 Oct  TEST TRANSACTION  100.00")]

    file_path = Path("/tmp/CardStatement_Oct2025.pdf")
    statement = CreditStatement(
        pages=pages,
        bank_name="Citibank",
        config=Citibank.credit,
        header="date description amount",
        file_path=file_path,
    )

    result_date = statement.statement_date
    assert result_date.year == 2025
    assert result_date.month == 10
    assert result_date.day == 1  # Fallback sets day to 1


def test_content_takes_precedence_over_filename():
    """Test that statement date from content takes precedence over filename."""
    pages_with_date = [
        PdfPage(raw_text="Statement Date 15 Nov 2022\nDATE  DESCRIPTION  AMOUNT\n15 Nov  TEST TRANSACTION  100.00")
    ]

    # Filename suggests December 2025, but content says November 15, 2022
    file_path = Path("/tmp/eStatement_Dec2025_2025-12-07T14_50_26.pdf")
    statement = CreditStatement(
        pages=pages_with_date,
        bank_name="Citibank",
        config=Citibank.credit,
        header="date description amount",
        file_path=file_path,
    )

    result_date = statement.statement_date
    # Should use the date from content, not filename
    assert result_date.year == 2022
    assert result_date.month == 11
    assert result_date.day == 15
