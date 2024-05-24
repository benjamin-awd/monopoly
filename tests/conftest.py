from unittest.mock import MagicMock, Mock, PropertyMock, patch

import fitz
import pytest

from monopoly.banks import Citibank, Dbs, Hsbc, Ocbc, StandardChartered
from monopoly.config import CreditStatementConfig, DateOrder, PdfConfig
from monopoly.handler import StatementHandler
from monopoly.pdf import PdfPage, PdfParser
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
        "monopoly.banks.base.BankBase.config",
        new_callable=PropertyMock,
    ) as mock_get_statement_config_prop:
        mock_get_statement_config_prop.return_value = None
        yield mock_get_statement_config


@pytest.fixture
def mock_document():
    with patch(
        "monopoly.pdf.PdfParser.document", new_callable=PropertyMock
    ) as mock_document_prop:
        mock_document_instance = mock_document_prop.return_value
        type(mock_document_instance).metadata = PropertyMock(
            return_value={
                "creator": "Adobe Acrobat 23.3",
                "producer": "Adobe Acrobat Pro (64-bit)",
            }
        )
        type(mock_document_instance).name = PropertyMock(return_value="foo")
        yield mock_document


@pytest.fixture(scope="function")
def handler():
    with patch.object(StatementHandler, "get_statement") as _:
        handler = StatementHandler(file_path="foo.pdf")
        yield handler


@pytest.fixture(scope="function")
def mock_bank():
    class MockBank:
        pdf_config = PdfConfig()
        passwords = None

    return MockBank()


@pytest.fixture
def parser(mock_bank):
    with patch(
        "monopoly.pdf.PdfParser.bank",
        new_callable=PropertyMock,
    ) as mock_bank_prop:
        mock_bank_prop.return_value = mock_bank
        parser = PdfParser(file_path=None)
        yield parser


def setup_statement_fixture(
    statement_cls: BaseStatement | DebitStatement | CreditStatement,
    monkeypatch,
    statement_config,
):
    mock_parser = MagicMock(spec=PdfParser)
    monkeypatch.setattr("monopoly.statements.base.BaseStatement.df", None)
    mock_page = Mock(spec=PdfPage)
    mock_page.lines = ["foo", "bar"]
    mock_page.raw_text = ["foo\nbar"]
    mock_parser.get_pages.return_value = [mock_page]

    document = MagicMock(spec=fitz.Document)
    document.name = "mock_document.pdf"
    statement = statement_cls(parser=mock_parser, config=statement_config)
    yield statement


@pytest.fixture(scope="function")
def credit_statement(monkeypatch, statement_config):
    yield from setup_statement_fixture(CreditStatement, monkeypatch, statement_config)


@pytest.fixture(scope="function")
def debit_statement(monkeypatch, statement_config):
    yield from setup_statement_fixture(DebitStatement, monkeypatch, statement_config)


@pytest.fixture(scope="function")
def statement(monkeypatch, parser, statement_config):
    yield from setup_statement_fixture(BaseStatement, monkeypatch, statement_config)


@pytest.fixture(scope="session")
def statement_config():
    statement_config = CreditStatementConfig(
        bank_name="example",
        transaction_pattern="foo",
        statement_date_pattern="",
        transaction_date_order=DateOrder("DMY"),
        prev_balance_pattern="foo",
    )
    yield statement_config
