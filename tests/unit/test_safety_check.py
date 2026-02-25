import re

import pytest
from pymupdf import Document

from monopoly.config import DateOrder, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.statements import CreditStatement, DebitStatement
from monopoly.statements.base import SafetyCheckError
from monopoly.statements.transaction import Transaction


def test_credit_safety_check(credit_statement: CreditStatement):
    document = Document()
    page = document.new_page()
    text = "Page 1\n3\nfoo\n02 May\n2.27\n27 Apr\n2.67\ntotal amount 31.50"
    page.lines = text.split("\n")
    page.insert_text(point=(0, 0), text=text)
    credit_statement.pages[0] = page

    credit_statement.document = document

    credit_statement.transactions = [
        Transaction(transaction_date="23/01", description="foo", amount=11.5),
        Transaction(transaction_date="24/01", description="bar", amount=20.0),
    ]

    # the safety check should return True, since the total amount of 31.50
    # is present in the text
    assert credit_statement.perform_safety_check()


def test_debit_safety_check(debit_statement: DebitStatement):
    document = Document()
    page = document.new_page()
    text = "Page 1\n3\nfoo\n02 May\n-2.5\n27 Apr\n2.67\ntotal credit 30.0 total debit 2.5"
    page.lines = text.split("\n")
    page.insert_text(point=(0, 0), text=text)
    debit_statement.pages[0] = page

    debit_statement.document = document

    debit_statement.transactions = [
        Transaction(transaction_date="23/01", description="foo", amount=10.0, polarity="CR"),
        Transaction(transaction_date="24/01", description="bar", amount=20.0, polarity="CR"),
        Transaction(transaction_date="25/01", description="baz", amount=-2.5, polarity="DR"),
    ]

    # the safety check should return True, since the credit sum matches
    # 10 + 20 = 30, and 2.5 is present in the statement
    assert debit_statement.perform_safety_check()


def test_debit_safety_check_failure(debit_statement: DebitStatement):
    document = Document()
    page = document.new_page()
    text = "Page 1\n3\nfoo\n02 May\n-999\n27 Apr\n456\nrandom transaction 123"
    page.lines = text.split("\n")
    page.insert_text(point=(0, 0), text=text)
    debit_statement.pages[0] = page

    debit_statement.document = document
    debit_statement.transactions = [
        Transaction(transaction_date="23/01", description="foo", amount=10.0, polarity="CR"),
        Transaction(transaction_date="24/01", description="bar", amount=20.0, polarity="CR"),
        Transaction(transaction_date="25/01", description="baz", amount=-2.5, polarity="DR"),
    ]

    # the safety check should fail, since the debit sum and credit sum
    # are not present as a number
    with pytest.raises(SafetyCheckError):
        debit_statement.perform_safety_check()


def test_safety_check_does_not_pass_when_total_not_in_document(credit_statement: CreditStatement):
    """
    This test guards against the old logic flaw where perform_safety_check()
    would incorrectly pass as long as the sum of transactions was positive,
    even if the total was not actually in the statement text.
    """

    # Create a dummy document with NO total value mentioned
    document = Document()
    page = document.new_page()
    text = "Statement Page 1\nTransaction A 10.00\nTransaction B 20.00\nNo totals listed here"
    page.lines = text.split("\n")
    page.insert_text(point=(0, 0), text=text)
    credit_statement.pages[0] = page
    credit_statement.document = document

    # Transactions sum to 30.00, but 30.00 is NOT in the document text.
    credit_statement.transactions = [
        Transaction(transaction_date="01/01", description="A", amount=10.0, polarity="CR"),
        Transaction(transaction_date="02/01", description="B", amount=20.0, polarity="CR"),
    ]

    # Old logic would wrongly return True — corrected logic should raise an error.
    with pytest.raises(SafetyCheckError):
        credit_statement.perform_safety_check()


def test_credit_safety_check_with_custom_subtotal_pattern():
    """Test that a multi-card statement passes safety check using custom subtotal_pattern.

    Simulates a Standard Chartered-style statement with two credit cards,
    where each card has a "NEW BALANCE" line but no combined total.
    """
    config = StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"Transaction.*Amount"),
        transaction_pattern=re.compile(
            r"(?P<transaction_date>\d{2} \w{3})\s+"
            r"(?P<description>.+?)\s+" + SharedPatterns.AMOUNT
        ),
        statement_date_pattern="",
        transaction_date_order=DateOrder("DMY"),
        subtotal_pattern=re.compile(
            rf"(?:NEW BALANCE.*?)\s+{SharedPatterns.AMOUNT}",
            re.IGNORECASE,
        ),
    )

    document = Document()
    page = document.new_page()
    text = (
        "Card 1 ending 1234\n"
        "01 Jan  GRAB TRANSPORT  15.00\n"
        "02 Jan  FAIRPRICE  25.50\n"
        "NEW BALANCE  40.50\n"
        "\n"
        "Card 2 ending 5678\n"
        "05 Jan  AMAZON  30.00\n"
        "NEW BALANCE  30.00\n"
    )
    page.lines = text.split("\n")
    page.insert_text(point=(0, 0), text=text)

    statement = CreditStatement(pages=[page], bank_name="standard_chartered", config=config, header="foo")
    statement.transactions = [
        Transaction(transaction_date="01/01", description="GRAB TRANSPORT", amount=15.0),
        Transaction(transaction_date="02/01", description="FAIRPRICE", amount=25.5),
        Transaction(transaction_date="05/01", description="AMAZON", amount=30.0),
    ]

    # Total is 70.50, which doesn't appear in the document.
    # But subtotals 40.50 + 30.00 = 70.50, so the safety check should pass.
    assert statement.perform_safety_check()
