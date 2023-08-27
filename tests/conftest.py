from datetime import datetime

import pytest

from monopoly.banks.ocbc import OCBC
from monopoly.gmail import Message
from monopoly.pdf import PDF, Statement


@pytest.fixture(scope="session")
def ocbc():
    ocbc = OCBC()
    yield ocbc


@pytest.fixture(scope="session")
def pdf():
    pdf = PDF()
    pdf.statement = Statement(
        bank="Example Bank",
        account_name="Savings",
        date=datetime(2023, 8, 1),
        filename="statement.csv",
        date_pattern=None,
        transaction_pattern=None,
    )

    yield pdf


@pytest.fixture(scope="session")
def message():
    return Message({})


@pytest.fixture(scope="session")
def attachment():
    return Message.Attachment(filename="test.pdf", file_byte_string=b"Test data")
