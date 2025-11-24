"""Test filename fallback for statement dates when not found in content."""

import re
from datetime import datetime
from pathlib import Path

import pytest

from monopoly.banks import Citibank
from monopoly.config import StatementConfig
from monopoly.constants import CreditTransactionPatterns, EntryType, StatementBalancePatterns
from monopoly.pdf import PdfPage
from monopoly.statements import CreditStatement


@pytest.mark.parametrize(
    "filename,expected_month",
    [
        ("eStatement_Nov2025_2025-11-07T14_50_26.pdf", 11),
        ("CardStatement_Oct2025.pdf", 10),
    ],
)
def test_filename_fallback_extracts_date(filename, expected_month):
    """Test that statement date can be extracted from filename patterns."""
    pages = [PdfPage(raw_text="DATE  DESCRIPTION  AMOUNT\n15 Nov  TEST TRANSACTION  100.00")]

    file_path = Path(f"/tmp/{filename}")
    statement = CreditStatement(
        pages=pages,
        bank_name="Citibank",
        config=Citibank.credit,
        header="date description amount",
        file_path=file_path,
    )

    result_date = statement.statement_date
    assert result_date.year == 2025
    assert result_date.month == expected_month
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


def test_filename_fallback_disabled_by_default():
    """Test that filename fallback is disabled when config doesn't have the pattern."""
    pages = [PdfPage(raw_text="DATE  DESCRIPTION  AMOUNT\n15 Nov  TEST TRANSACTION  100.00")]

    # Create a config without filename_fallback_pattern
    config_without_fallback = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(r"Statement\sDate\s+(.*)"),
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        transaction_date_format="%d %b",
        prev_balance_pattern=StatementBalancePatterns.CITIBANK,
        transaction_pattern=CreditTransactionPatterns.CITIBANK,
        # Note: no filename_fallback_pattern set
    )

    file_path = Path("/tmp/eStatement_Nov2025_2025-11-07T14_50_26.pdf")
    statement = CreditStatement(
        pages=pages,
        bank_name="Citibank",
        config=config_without_fallback,
        header="date description amount",
        file_path=file_path,
    )

    # Should raise ValueError since no statement date in content and fallback disabled
    with pytest.raises(ValueError, match="Statement date not found"):
        _ = statement.statement_date
