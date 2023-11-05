import fitz
import pandas as pd

from monopoly.banks import BankBase
from monopoly.statement import Statement


class MockBank(BankBase):
    statement_config = None
    transaction_config = None
    safety_check_enabled = True


def test_safety_check(statement: Statement):
    bank = MockBank(file_path="foo")
    document = fitz.Document()
    page = document.new_page()
    text = "Page 1\n3\nfoo\n02 May\n2.27\n27 Apr\n2.67\ntotal amount 31.50"
    page.insert_text(point=(0, 0), text=text)
    statement.pages[0] = page

    bank.document = document

    statement.df = pd.DataFrame(data={"amount": [11.5, 20.0]})

    # the safety check should return True, since the total amount of 31.50
    # is present in the text
    assert bank._perform_safety_check(statement)
