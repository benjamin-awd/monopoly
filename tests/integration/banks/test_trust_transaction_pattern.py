"""Unit tests for Trust bank transaction pattern parsing."""

import pytest

from monopoly.banks import Trust
from monopoly.pdf import PdfPage
from monopoly.statements import BaseStatement
from monopoly.statements.transaction import Transaction


@pytest.fixture
def statement(statement: BaseStatement):
    """Configure statement with Trust credit card pattern."""
    statement.config = Trust.credit
    return statement


def test_trust_single_line_transaction(statement: BaseStatement):
    """Test single-line transaction where posting date is on the same line.

    Example: 21 Oct 24 Oct SP Services 225.77
    Should extract: transaction_date=21 Oct, description=SP Services, amount=225.77
    The posting date (24 Oct) should be skipped.
    """
    statement.pages = [PdfPage("21 Oct 24 Oct SP Services 225.77")]
    transactions = statement.get_transactions()

    expected = [
        Transaction(
            transaction_date="21 Oct",
            description="SP Services",
            amount=-225.77,
            polarity=None,
        )
    ]
    assert transactions == expected


def test_trust_transaction_with_fcy(statement: BaseStatement):
    """Test transaction with foreign currency (FCY) amount.

    Example: 20 Oct 22 Oct Google 9.99 USD 12.96
    Should extract: transaction_date=20 Oct, description=Google, amount=12.96
    The posting date (22 Oct) and FCY amount (9.99 USD) should be skipped.
    """
    statement.pages = [PdfPage("20 Oct 22 Oct Google 9.99 USD 12.96")]
    transactions = statement.get_transactions()

    expected = [
        Transaction(
            transaction_date="20 Oct",
            description="Google 9.99 USD",
            amount=-12.96,
            polarity=None,
        )
    ]
    assert transactions == expected


def test_trust_multiline_transaction_no_fcy(statement: BaseStatement):
    """Test multiline transaction without FCY.

    Example: 19 Oct 23 Oct NEX FJ-ZHEN SHI KOREAN
                                SINGAPORE SG 7.20
    Should extract: transaction_date=19 Oct,
                   description=NEX FJ-ZHEN SHI KOREAN SINGAPORE SG,
                   amount=7.20
    The posting date (23 Oct) should be skipped.
    """
    statement.pages = [PdfPage("19 Oct 23 Oct NEX FJ-ZHEN SHI KOREAN SINGAPORE SG 7.20")]
    transactions = statement.get_transactions()

    expected = [
        Transaction(
            transaction_date="19 Oct",
            description="NEX FJ-ZHEN SHI KOREAN SINGAPORE SG",
            amount=-7.20,
            polarity=None,
        )
    ]
    assert transactions == expected


def test_trust_multiple_transactions(statement: BaseStatement):
    """Test multiple transactions in sequence."""
    statement.pages = [
        PdfPage(
            "21 Oct 24 Oct SP Services 225.77\n"
            "20 Oct 22 Oct Google 9.99 USD 12.96\n"
            "19 Oct 23 Oct NEX FJ-ZHEN SHI KOREAN SINGAPORE SG 7.20"
        )
    ]
    transactions = statement.get_transactions()

    expected = [
        Transaction(
            transaction_date="21 Oct",
            description="SP Services",
            amount=-225.77,
            polarity=None,
        ),
        Transaction(
            transaction_date="20 Oct",
            description="Google 9.99 USD",
            amount=-12.96,
            polarity=None,
        ),
        Transaction(
            transaction_date="19 Oct",
            description="NEX FJ-ZHEN SHI KOREAN SINGAPORE SG",
            amount=-7.20,
            polarity=None,
        ),
    ]
    assert transactions == expected


def test_trust_transaction_with_refund(statement: BaseStatement):
    """Test transaction with positive polarity (refund/credit).

    Example: 15 Oct 17 Oct REFUND +50.00
    Should extract: transaction_date=15 Oct, description=REFUND, amount=50.00, polarity=+
    """
    statement.pages = [PdfPage("15 Oct 17 Oct REFUND +50.00")]
    transactions = statement.get_transactions()

    expected = [
        Transaction(
            transaction_date="15 Oct",
            description="REFUND",
            amount=50.0,
            polarity="+",
        )
    ]
    assert transactions == expected


def test_trust_transaction_with_decimal_fcy(statement: BaseStatement):
    """Test transaction with FCY amount that has decimals.

    Example: 18 Oct 20 Oct Amazon 49.99 USD 64.85
    Should extract: transaction_date=18 Oct, description=Amazon, amount=64.85
    """
    statement.pages = [PdfPage("18 Oct 20 Oct Amazon 49.99 USD 64.85")]
    transactions = statement.get_transactions()

    expected = [
        Transaction(
            transaction_date="18 Oct",
            description="Amazon 49.99 USD",
            amount=-64.85,
            polarity=None,
        )
    ]
    assert transactions == expected
