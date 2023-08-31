from datetime import datetime

import pytest

from monopoly.banks.dataclasses import Bank, Statement
from monopoly.banks.ocbc.credit import Ocbc365
from monopoly.gmail import Message
from monopoly.pdf import PdfParser


@pytest.fixture(scope="session")
def ocbc():
    ocbc = Ocbc365(pdf_file_path="tests/fixtures/ocbc/input.pdf")
    yield ocbc


@pytest.fixture(scope="session")
def bank():
    bank = Bank(
        account_name="Savings",
        bank="Example Bank",
        statement=Statement(
            transaction_pattern=None,
            date_pattern=None,
            statement_date=datetime(2023, 8, 1),
        ),
        pdf=None,
    )

    yield bank


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
