from typing import Type
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import fitz
import pytest

from monopoly.banks import BankBase
from monopoly.config import CreditStatementConfig, DateOrder, PdfConfig
from monopoly.handler import StatementHandler
from monopoly.pdf import PdfPage, PdfParser
from monopoly.statements import BaseStatement, CreditStatement, DebitStatement


@pytest.fixture
def mock_get_pages():
    with patch.object(PdfParser, "get_pages") as mock_get_pages:
        mock_get_pages.return_value = MagicMock()
        yield mock_get_pages


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
def handler(mock_bank: Type[BankBase], parser):
    with patch.object(StatementHandler, "get_statement") as _:
        handler = StatementHandler(mock_bank, parser)
        yield handler


@pytest.fixture(scope="function")
def mock_bank():
    class MockBank:
        pdf_config = PdfConfig()
        passwords = None

    return MockBank()


@pytest.fixture
def parser():
    parser = PdfParser(file_path=None)
    yield parser


def setup_statement_fixture(
    statement_cls: BaseStatement | DebitStatement | CreditStatement,
    mock_bank: Type[BankBase],
    statement_config,
):
    mock_parser = MagicMock(spec=PdfParser)
    mock_page = Mock(spec=PdfPage)
    mock_page.lines = ["foo", "bar"]
    mock_page.raw_text = ["foo\nbar"]
    mock_parser.get_pages.return_value = [mock_page]

    document = MagicMock(spec=fitz.Document)
    document.name = "mock_document.pdf"
    statement = statement_cls(bank=mock_bank, parser=mock_parser, config=statement_config)
    yield statement


@pytest.fixture(scope="function")
def credit_statement(mock_bank: Type[BankBase], statement_config):
    yield from setup_statement_fixture(CreditStatement, mock_bank, statement_config)


@pytest.fixture(scope="function")
def debit_statement(mock_bank: Type[BankBase], statement_config):
    yield from setup_statement_fixture(DebitStatement, mock_bank, statement_config)


@pytest.fixture(scope="function")
def statement(mock_bank: Type[BankBase],statement_config):
    yield from setup_statement_fixture(BaseStatement, mock_bank, statement_config)


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


@pytest.fixture
def no_banks(monkeypatch):
    monkeypatch.setattr("monopoly.banks.banks", [])
