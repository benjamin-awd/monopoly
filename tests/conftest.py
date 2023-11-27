from datetime import datetime
from unittest import mock
from unittest.mock import PropertyMock

import pytest

from monopoly.config import StatementConfig, TransactionConfig
from monopoly.constants import AccountType, BankNames
from monopoly.pdf import PdfPage, PdfParser
from monopoly.processor import StatementProcessor
from monopoly.processors import Citibank, Dbs, Hsbc, Ocbc, StandardChartered
from monopoly.statement import Statement


@pytest.fixture(scope="session")
def citibank():
    citibank = Citibank(file_path="tests/integration/fixtures/citibank/input.pdf")
    yield citibank


@pytest.fixture(scope="session")
def dbs():
    dbs = Dbs(file_path="tests/integration/fixtures/dbs/input.pdf")
    yield dbs


@pytest.fixture(scope="session")
def ocbc():
    ocbc = Ocbc(file_path="tests/integration/fixtures/ocbc/input.pdf")
    yield ocbc


@pytest.fixture(scope="session")
def hsbc():
    hsbc = Hsbc(file_path="tests/integration/fixtures/hsbc/input.pdf")
    yield hsbc


@pytest.fixture(scope="session")
def standard_chartered():
    standard_chartered = StandardChartered(
        file_path="tests/integration/fixtures/standard_chartered/input.pdf"
    )
    yield standard_chartered


@pytest.fixture(scope="function")
def processor(statement_config, transaction_config):
    with mock.patch.object(
        Statement, "statement_date", new_callable=PropertyMock
    ) as mock_statement_date:
        mock_statement_date.return_value = datetime(2023, 8, 1)
        processor = StatementProcessor(
            statement_config=statement_config,
            transaction_config=transaction_config,
            pdf_config=None,
            file_path="foo",
        )
        yield processor


@pytest.fixture(scope="function")
def parser():
    parser = PdfParser(file_path=None)
    yield parser


@pytest.fixture(scope="function")
def statement(monkeypatch, statement_config, transaction_config):
    monkeypatch.setattr("monopoly.processor.Statement.df", None)
    mock_page = mock.Mock(spec=PdfPage)
    statement = Statement(
        pages=[mock_page],
        statement_config=statement_config,
        transaction_config=transaction_config,
    )
    yield statement


@pytest.fixture(scope="session")
def statement_config():
    statement_config = StatementConfig(
        account_type=AccountType.CREDIT,
        bank_name=BankNames.OCBC,
        date_format=r"%d-%m-%Y",
        transaction_pattern="foo",
        transaction_date_format=r"%d/%m",
        date_pattern="",
        prev_balance_pattern="foo",
    )
    yield statement_config


@pytest.fixture(scope="session")
def transaction_config():
    transaction_config = TransactionConfig(
        pattern="foo",
        date_format=r"%d/%m",
    )
    yield transaction_config
