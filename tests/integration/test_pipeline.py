from datetime import date
from pathlib import Path

import pytest

from monopoly.banks import Dbs
from monopoly.examples.example_bank import ExampleBank
from monopoly.pdf import PdfDocument, PdfParser
from monopoly.pipeline import Pipeline


@pytest.fixture
def pdf_file_bytes():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    with file_path.open("rb") as f:
        yield f.read()


def test_pipeline_with_bank():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    document = PdfDocument(file_path)
    parser = PdfParser(ExampleBank, document)
    pipeline = Pipeline(parser)
    pages = parser._get_pages()
    transactions = pipeline.extract(pages).transactions
    assert len(transactions) == 53
    assert transactions[0].description == "LAST MONTH'S BALANCE"


def test_pipeline_stamps_config_currency(monkeypatch):
    # currency lives on the matched StatementConfig, not the bank class
    monkeypatch.setattr(ExampleBank.credit, "currency", "SGD")
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    document = PdfDocument(file_path)
    parser = PdfParser(ExampleBank, document)
    pipeline = Pipeline(parser)
    transactions = pipeline.extract(parser._get_pages()).transactions
    assert transactions
    assert all(tx.currency == "SGD" for tx in transactions)


def test_pipeline_extracts_payment_summary():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    document = PdfDocument(file_path)
    parser = PdfParser(ExampleBank, document)
    pipeline = Pipeline(parser)
    statement = pipeline.extract(parser._get_pages())

    summary = statement.payment_summary
    assert summary.payment_due_date == date(2023, 8, 24)
    assert summary.total_amount_due == 702.10
    assert summary.minimum_payment == 50.00


def test_pipeline_with_bad_bank():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    document = PdfDocument(file_path)
    parser = PdfParser(Dbs, document)
    pipeline = Pipeline(parser)
    pages = parser._get_pages()

    with pytest.raises(ValueError, match="No transactions found"):
        pipeline.extract(pages)


def test_pipeline_initialization_with_file_path():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    try:
        document = PdfDocument(file_path)
        parser = PdfParser(ExampleBank, document)
        pipeline = Pipeline(parser)
        pages = parser._get_pages()
        statement = pipeline.extract(pages)
        transactions = pipeline.transform(statement)
        assert len(transactions) == 53
        # ExampleBank sets no currency, so it stays None (default)
        assert all(tx.currency is None for tx in transactions)
    except RuntimeError as e:
        pytest.fail(f"Pipeline initialization failed with RuntimeError: {e}")


def test_pipeline_bytes_etl(pdf_file_bytes):
    document = PdfDocument(file_bytes=pdf_file_bytes)
    parser = PdfParser(ExampleBank, document)
    pipeline = Pipeline(parser)

    pages = parser._get_pages()
    statement = pipeline.extract(pages)
    transactions = pipeline.transform(statement)
    assert len(transactions) == 53
