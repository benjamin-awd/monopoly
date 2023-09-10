from datetime import datetime
from unittest import mock
from unittest.mock import PropertyMock

import pytest

from monopoly.banks.bank import Bank, Statement, StatementConfig
from monopoly.banks.citibank.credit import Citibank
from monopoly.banks.hsbc.credit import Hsbc
from monopoly.banks.ocbc.credit import Ocbc
from monopoly.gmail import Message, MessageAttachment
from monopoly.pdf import PdfConfig, PdfParser


@pytest.fixture(scope="session")
def citibank():
    citibank = Citibank(file_path="tests/fixtures/citibank/input.pdf")
    yield citibank


@pytest.fixture(scope="session")
def ocbc():
    ocbc = Ocbc(file_path="tests/fixtures/ocbc/input.pdf")
    yield ocbc


@pytest.fixture(scope="session")
def hsbc():
    hsbc = Hsbc(file_path="tests/fixtures/hsbc/input.pdf")
    yield hsbc


@pytest.fixture(scope="function")
def bank(statement_config):
    with mock.patch.object(
        Statement, "statement_date", new_callable=PropertyMock
    ) as mock_statement_date:
        mock_statement_date.return_value = datetime(2023, 8, 1)
        bank = Bank(statement_config=statement_config, pdf_config=None, file_path="foo")
        yield bank


@pytest.fixture(scope="session")
def message():
    return Message(data={}, gmail_service=mock.Mock())


@pytest.fixture(scope="session")
def attachment():
    return MessageAttachment(filename="test.pdf", file_byte_string=b"Test data")


@pytest.fixture(scope="session")
def parser():
    parser = PdfParser(None, config=PdfConfig(None))
    yield parser


@pytest.fixture(scope="function")
def statement(monkeypatch, statement_config):
    monkeypatch.setattr("monopoly.banks.statement.Statement.df", None)
    mock_page = mock.Mock()
    statement = Statement(pages=[mock_page], config=statement_config)
    yield statement


@pytest.fixture(scope="session")
def statement_config():
    statement_config = StatementConfig(
        account_type="Savings",
        bank_name="Example Bank",
        statement_date_format=None,
        transaction_pattern=None,
        transaction_date_format=None,
        date_pattern=None,
    )
    yield statement_config
