from datetime import datetime

import pytest

from monopoly.banks.ocbc.credit import Ocbc365
from monopoly.banks.statement import BankStatement
from monopoly.gmail import Message
from monopoly.pdf import PdfParser


@pytest.fixture(scope="session")
def ocbc():
    ocbc = Ocbc365(pdf_file_path="tests/ocbc/fixtures/input.pdf")
    yield ocbc


@pytest.fixture(scope="session")
def bank_statement():
    bank_statement = BankStatement(
        account_name="Savings",
        bank="Example Bank",
        date_pattern=None,
        pdf_file_path=None,
        pdf_password=None,
        transaction_pattern=None,
        transform_dates=False,
    )
    bank_statement.statement_date = datetime(2023, 8, 1)
    bank_statement.filename = "statement.csv"

    yield bank_statement


@pytest.fixture(scope="session")
def message():
    return Message({})


@pytest.fixture(scope="session")
def attachment():
    return Message.Attachment(filename="test.pdf", file_byte_string=b"Test data")


@pytest.fixture(scope="session")
def parser():
    parser = PdfParser(None)

    yield parser
