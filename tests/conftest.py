from datetime import datetime
from unittest import mock
from unittest.mock import PropertyMock

import pytest

from monopoly.banks import Citibank, Hsbc, Ocbc, StandardChartered
from monopoly.config import StatementConfig
from monopoly.constants import AccountType, BankNames
from monopoly.gmail import Message, MessageAttachment
from monopoly.pdf import PdfPage, PdfParser
from monopoly.processor import StatementProcessor
from monopoly.statement import Statement


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


@pytest.fixture(scope="session")
def standard_chartered():
    standard_chartered = StandardChartered(
        file_path="tests/integration/fixtures/standard_chartered/input.pdf"
    )
    yield standard_chartered


@pytest.fixture(scope="function")
def processor(statement_config):
    with mock.patch.object(
        Statement, "statement_date", new_callable=PropertyMock
    ) as mock_statement_date:
        mock_statement_date.return_value = datetime(2023, 8, 1)
        processor = StatementProcessor(
            statement_config=statement_config, pdf_config=None, file_path="foo"
        )
        yield processor


@pytest.fixture(scope="session")
def message():
    return Message(data={}, gmail_service=mock.Mock())


@pytest.fixture(scope="session")
def attachment():
    return MessageAttachment(filename="test.pdf", file_byte_string=b"Test data")


@pytest.fixture(scope="session")
def parser():
    parser = PdfParser(file_path=None)
    yield parser


@pytest.fixture(scope="function")
def statement(monkeypatch, statement_config):
    monkeypatch.setattr("monopoly.processor.Statement.df", None)
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
