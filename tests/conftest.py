from datetime import datetime
from unittest import mock
from unittest.mock import PropertyMock

import pytest

from monopoly.banks.bank import Bank, Statement
from monopoly.banks.hsbc.credit import HsbcRevolution
from monopoly.banks.ocbc.credit import Ocbc365
from monopoly.gmail import Gmail, Message
from monopoly.pdf import PdfParser


@pytest.fixture(scope="function")
def date_specific_ocbc(statement, statement_date: datetime):
    with mock.patch.object(
        Statement, "statement_date", new_callable=PropertyMock
    ) as mock_statement_date:
        mock_statement_date.return_value = statement_date
        ocbc = Ocbc365(pdf_file_path="tests/fixtures/ocbc/input.pdf")
        ocbc.statement = statement
        yield ocbc


@pytest.fixture(scope="function")
def date_specific_hsbc(statement, statement_date: datetime):
    with mock.patch.object(
        Statement, "statement_date", new_callable=PropertyMock
    ) as mock_statement_date:
        mock_statement_date.return_value = statement_date
        hsbc = HsbcRevolution(pdf_file_path="tests/fixtures/hsbc/input.pdf")
        hsbc.statement = statement
        yield hsbc


@pytest.fixture(scope="session")
def generic_ocbc():
    ocbc = Ocbc365(pdf_file_path="tests/fixtures/ocbc/input.pdf")
    yield ocbc


@pytest.fixture(scope="session")
def generic_hsbc():
    hsbc = HsbcRevolution(pdf_file_path="tests/fixtures/hsbc/input.pdf")
    yield hsbc


@pytest.fixture(scope="function")
def bank(statement):
    with mock.patch.object(
        Statement, "statement_date", new_callable=PropertyMock
    ) as mock_statement_date:
        mock_statement_date.return_value = datetime(2023, 8, 1)
        bank = Bank(
            account_name="Savings",
            bank_name="Example Bank",
            statement=statement,
            pdf=None,
        )
        yield bank


@pytest.fixture(scope="session")
def message():
    return Message(data={}, gmail_service=mock.Mock())


@pytest.fixture(scope="session")
def attachment():
    return Message.Attachment(filename="test.pdf", file_byte_string=b"Test data")


@pytest.fixture(scope="session")
def parser():
    parser = PdfParser(None)

    yield parser


@pytest.fixture
def statement():
    mock_page = mock.Mock()
    statement = Statement(
        statement_date_format=None,
        transaction_pattern=None,
        date_pattern=None,
        pages=[mock_page],
    )
    yield statement
