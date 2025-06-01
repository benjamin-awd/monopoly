import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from pymupdf import Document

from monopoly.banks.detector import BankDetector
from monopoly.config import DateOrder, PdfConfig, StatementConfig
from monopoly.constants import EntryType
from monopoly.handler import StatementHandler
from monopoly.pdf import PdfDocument, PdfPage, PdfParser
from monopoly.statements import BaseStatement, CreditStatement, DebitStatement


@pytest.fixture
def mock_env():
    """Prevents existing environment variables from interfering with tests"""
    with patch.dict(os.environ, clear=True):
        yield


@pytest.fixture
def pdf_document():
    yield PdfDocument(file_path="src/monopoly/examples/example_statement.pdf")


@pytest.fixture
def metadata_analyzer(pdf_document):
    yield BankDetector(pdf_document)


@pytest.fixture
def mock_get_pages():
    with patch.object(PdfParser, "get_pages") as mock_get_pages:
        mock_get_pages.return_value = MagicMock()
        yield mock_get_pages


@pytest.fixture(scope="function")
def handler(parser):
    with patch.object(StatementHandler, "get_statement") as _:
        handler = StatementHandler(parser)
        yield handler


@pytest.fixture(scope="function")
def mock_bank():
    class MockBank:
        pdf_config = PdfConfig()
        passwords = None

    return MockBank()


@pytest.fixture
def parser(mock_bank):
    class MockDocument:
        metadata_identifier = [None]

    document = MockDocument()
    parser = PdfParser(bank=mock_bank, document=document)
    yield parser


def setup_statement_fixture(
    statement_cls: BaseStatement,
    statement_config,
):
    mock_page = Mock(spec=PdfPage)
    mock_page.lines = ["foo", "bar"]
    mock_page.raw_text = ["foo\nbar"]
    document = MagicMock(spec=Document)
    document.name = "mock_document.pdf"
    statement = statement_cls(pages=[mock_page], bank_name="example", config=statement_config, header="foo")
    yield statement


@pytest.fixture(scope="function")
def credit_statement(statement_config):
    yield from setup_statement_fixture(CreditStatement, statement_config)


@pytest.fixture(scope="function")
def debit_statement(statement_config):
    yield from setup_statement_fixture(DebitStatement, statement_config)


@pytest.fixture(scope="function")
def statement(statement_config):
    yield from setup_statement_fixture(BaseStatement, statement_config)


@pytest.fixture(scope="session")
def statement_config():
    statement_config = StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern="foo",
        transaction_pattern="foo",
        statement_date_pattern="",
        transaction_date_order=DateOrder("DMY"),
        prev_balance_pattern="foo",
    )
    yield statement_config


@pytest.fixture
def no_banks(monkeypatch):
    monkeypatch.setattr("monopoly.banks.banks", [])
