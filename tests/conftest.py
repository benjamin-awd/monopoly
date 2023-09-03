from datetime import datetime
from unittest import mock
from unittest.mock import PropertyMock

import pytest

from monopoly.banks.bank import Bank, Statement, StatementConfig
from monopoly.banks.hsbc.credit import HsbcRevolution
from monopoly.banks.ocbc.credit import Ocbc365
from monopoly.gmail import Message
from monopoly.pdf import PdfParser


def setup_mock_transactions(statement, transactions_data, date_specific_hsbc):
    with mock.patch.object(
        Statement, "transactions", new_callable=PropertyMock
    ) as mock_transactions:
        mock_transactions.return_value = transactions_data
        transformed_df = date_specific_hsbc.transform(statement)
    return transformed_df


@pytest.fixture(scope="session")
def ocbc():
    ocbc = Ocbc365(pdf_file_path="tests/fixtures/ocbc/input.pdf")
    yield ocbc


@pytest.fixture(scope="session")
def hsbc():
    hsbc = HsbcRevolution(pdf_file_path="tests/fixtures/hsbc/input.pdf")
    yield hsbc


@pytest.fixture(scope="function")
def bank():
    with mock.patch.object(
        Statement, "statement_date", new_callable=PropertyMock
    ) as mock_statement_date:
        mock_statement_date.return_value = datetime(2023, 8, 1)
        bank = Bank(
            account_name="Savings",
            bank_name="Example Bank",
            statement_config=None,
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


@pytest.fixture(scope="function")
def statement():
    mock_page = mock.Mock()
    statement_config = StatementConfig(
        statement_date_format=None,
        transaction_pattern=None,
        date_pattern=None,
    )
    statement = Statement(pages=[mock_page], config=statement_config)
    yield statement
