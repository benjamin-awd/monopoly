import fitz
import pandas as pd

from monopoly.processors import ProcessorBase
from monopoly.statement import Statement


class MockProcessor(ProcessorBase):
    credit_config = None
    debit_config = None


def test_safety_check(statement: Statement):
    mock_processor = MockProcessor(file_path="foo")
    document = fitz.Document()
    page = document.new_page()
    text = "Page 1\n3\nfoo\n02 May\n2.27\n27 Apr\n2.67\ntotal amount 31.50"
    page.lines = text.split("\n")
    page.insert_text(point=(0, 0), text=text)
    statement.pages[0] = page

    mock_processor.document = document

    statement.df = pd.DataFrame(data={"amount": [11.5, 20.0]})

    # the safety check should return True, since the total amount of 31.50
    # is present in the text
    assert mock_processor._perform_safety_check(statement)
