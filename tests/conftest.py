from datetime import datetime
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

from monopoly.config import CreditStatementConfig
from monopoly.constants import AccountType, BankNames
from monopoly.pdf import PdfPage, PdfParser
from monopoly.processor import StatementProcessor
from monopoly.processors import Citibank, Dbs, Hsbc, Ocbc, StandardChartered
from monopoly.statements import BaseStatement, CreditStatement, DebitStatement


@pytest.fixture(scope="session")
def citibank():
    citibank = Citibank(file_path="tests/integration/banks/citibank/credit/input.pdf")
    yield citibank


@pytest.fixture(scope="session")
def dbs():
    dbs = Dbs(file_path="tests/integration/banks/dbs/credit/input.pdf")
    yield dbs


@pytest.fixture(scope="session")
def ocbc():
    ocbc = Ocbc(file_path="tests/integration/banks/ocbc/credit/input.pdf")
    yield ocbc


@pytest.fixture(scope="session")
def hsbc():
    hsbc = Hsbc(file_path="tests/integration/banks/hsbc/credit/input.pdf")
    yield hsbc


@pytest.fixture(scope="session")
def standard_chartered():
    standard_chartered = StandardChartered(
        file_path="tests/integration/banks/standard_chartered/credit/input.pdf"
    )
    yield standard_chartered


@pytest.fixture
def mock_get_pages():
    with patch.object(PdfParser, "get_pages") as mock_get_pages:
        mock_get_pages.return_value = MagicMock()
        yield mock_get_pages


@pytest.fixture
def mock_get_statement_config():
    with patch(
        "monopoly.processors.base.ProcessorBase.statement_config",
        new_callable=PropertyMock,
    ) as mock_get_statement_config:
        mock_get_statement_config.return_value = None
        yield mock_get_statement_config


@pytest.fixture
def mock_document():
    with patch(
        "monopoly.pdf.PdfParser.document", new_callable=PropertyMock
    ) as mock_document:
        mock_document_instance = mock_document.return_value
        # Set the metadata attribute to the desired value
        type(mock_document_instance).metadata = PropertyMock(
            return_value={
                "creator": "Adobe Acrobat 23.3",
                "producer": "Adobe Acrobat Pro (64-bit)",
            }
        )
        yield mock_document


@pytest.fixture(scope="function")
def processor(statement_config):
    with patch.object(
        BaseStatement, "statement_date", new_callable=PropertyMock
    ) as mock_statement_date:
        mock_statement_date.return_value = datetime(2023, 8, 1)
        processor = StatementProcessor(
            statement_config=statement_config,
            pdf_config=None,
            file_path="foo",
        )
        yield processor


@pytest.fixture(scope="function")
def parser():
    parser = PdfParser(file_path=None)
    yield parser


@pytest.fixture(scope="function")
def credit_statement(monkeypatch, statement_config):
    monkeypatch.setattr("monopoly.statements.base.BaseStatement.df", None)
    mock_page = Mock(spec=PdfPage)
    mock_page.lines = ["foo\nbar"]
    statement = CreditStatement(
        document=None, pages=[mock_page], credit_config=statement_config
    )
    yield statement


@pytest.fixture(scope="function")
def debit_statement(monkeypatch, statement_config):
    monkeypatch.setattr("monopoly.statements.base.BaseStatement.df", None)
    mock_page = Mock(spec=PdfPage)
    mock_page.lines = ["foo\nbar"]
    statement = DebitStatement(
        document=None, pages=[mock_page], debit_config=statement_config
    )
    yield statement


@pytest.fixture(scope="function")
def statement(monkeypatch, statement_config):
    monkeypatch.setattr("monopoly.statements.base.BaseStatement.df", None)
    mock_page = MagicMock(spec=PdfPage)
    mock_page.lines = ["foo\nbar"]
    statement = BaseStatement(
        pages=[mock_page],
        document=None,
        statement_config=statement_config,
    )
    yield statement


@pytest.fixture(scope="session")
def statement_config():
    statement_config = CreditStatementConfig(
        account_type=AccountType.CREDIT,
        bank_name=BankNames.OCBC,
        statement_date_format=r"%d-%m-%Y",
        transaction_pattern="foo",
        transaction_date_format=r"%d/%m",
        statement_date_pattern="",
        prev_balance_pattern="foo",
        debit_statement_identifier="debitidentifier123",
    )
    yield statement_config
