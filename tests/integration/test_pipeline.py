from pathlib import Path

import pytest

from monopoly.banks import Dbs, ExampleBank
from monopoly.pipeline import Pipeline


@pytest.fixture
def pdf_file_bytes():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    with file_path.open("rb") as f:
        yield f.read()


def test_pipeline_initialization_with_bytes(pdf_file_bytes):
    try:
        pipeline = Pipeline(file_bytes=pdf_file_bytes)
        assert pipeline is not None
    except RuntimeError as e:
        pytest.fail(f"Pipeline initialization failed with RuntimeError: {e}")


def test_pipeline_with_bank():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    pipeline = Pipeline(file_path=file_path, bank=ExampleBank)
    transactions = pipeline.statement.transactions
    assert len(transactions) == 53
    assert transactions[0].description == "LAST MONTH'S BALANCE"


def test_pipeline_with_bad_bank():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    pipeline = Pipeline(file_path=file_path, bank=Dbs)
    with pytest.raises(ValueError, match="Statement date not found"):
        pipeline.extract()


def test_pipeline_initialization_with_file_path():
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    try:
        pipeline = Pipeline(file_path=file_path)
        assert pipeline is not None
    except RuntimeError as e:
        pytest.fail(f"Pipeline initialization failed with RuntimeError: {e}")


def test_pipeline_initialization_with_both_raises_error(pdf_file_bytes):
    file_path = Path("src/monopoly/examples/example_statement.pdf")
    with pytest.raises(
        RuntimeError, match="Only one of `file_path` or `file_bytes` should be passed"
    ):
        Pipeline(file_path=file_path, file_bytes=pdf_file_bytes)


def test_pipeline_initialization_with_neither_raises_error():
    with pytest.raises(
        RuntimeError, match="Either `file_path` or `file_bytes` must be passed"
    ):
        Pipeline()


def test_pipeline_bytes_etl(pdf_file_bytes):
    pipeline = Pipeline(file_bytes=pdf_file_bytes)
    statement = pipeline.extract()
    transactions = pipeline.transform(statement)
    assert len(transactions) == 53
