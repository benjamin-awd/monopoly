import fitz
import pandas as pd

from monopoly.processors import ProcessorBase
from monopoly.statements import CreditStatement, DebitStatement


class MockProcessor(ProcessorBase):
    credit_config = None
    debit_config = None


def test_credit_safety_check(credit_statement: CreditStatement):
    document = fitz.Document()
    page = document.new_page()
    text = "Page 1\n3\nfoo\n02 May\n2.27\n27 Apr\n2.67\ntotal amount 31.50"
    page.lines = text.split("\n")
    page.insert_text(point=(0, 0), text=text)
    credit_statement.pages[0] = page

    credit_statement.document = document

    credit_statement.df = pd.DataFrame(data={"amount": [11.5, 20.0]})

    # the safety check should return True, since the total amount of 31.50
    # is present in the text
    assert credit_statement.perform_safety_check()


def test_debit_safety_check(debit_statement: DebitStatement):
    document = fitz.Document()
    page = document.new_page()
    text = "Page 1\n3\nfoo\n02 May\n-2.5\n27 Apr\n2.67\nrandom transaction 31.50"
    page.lines = text.split("\n")
    page.insert_text(point=(0, 0), text=text)
    debit_statement.pages[0] = page

    debit_statement.document = document

    debit_statement.df = pd.DataFrame(data={"amount": [11.5, 20.0, -2.5]})

    # the safety check should return True, since the total amount of 31.50
    # is present in the text
    assert debit_statement.perform_safety_check()
