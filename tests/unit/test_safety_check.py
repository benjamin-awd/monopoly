import pytest
from pymupdf import Document

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
