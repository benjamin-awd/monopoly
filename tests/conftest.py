from datetime import datetime
from unittest import mock
from unittest.mock import PropertyMock

import pytest

from monopoly.bank import Bank, Statement, StatementConfig
from monopoly.banks import Citibank, Hsbc, Ocbc
from monopoly.constants import AccountType, BankNames
from monopoly.gmail import Message, MessageAttachment
from monopoly.pdf import PdfConfig, PdfPage, PdfParser


@pytest.fixture(scope="session")
def citibank():
    citibank = Citibank(file_path="tests/integration/fixtures/citibank/input.pdf")
    yield citibank


@pytest.fixture(scope="session")
def ocbc():
    ocbc = Ocbc(file_path="tests/integration/fixtures/ocbc/input.pdf")
    yield ocbc


@pytest.fixture(scope="session")
def hsbc():
    hsbc = Hsbc(file_path="tests/integration/fixtures/hsbc/input.pdf")
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
    monkeypatch.setattr("monopoly.bank.Statement.df", None)
    mock_page = mock.Mock(spec=PdfPage)
    statement = Statement(pages=[mock_page], config=statement_config)
    yield statement


@pytest.fixture(scope="session")
def statement_config():
    statement_config = StatementConfig(
        account_type=AccountType.CREDIT,
        bank_name=BankNames.OCBC,
        statement_date_format=r"%d-%m-%Y",
        transaction_pattern="foo",
        transaction_date_format=r"%d/%m",
        statement_date_pattern="",
    )
    yield statement_config
