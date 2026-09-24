"""
Pin the public `Pipeline` call shapes that library users rely on.

Callers that drive `Pipeline` directly rather than through the CLI break on a
signature change that no other test would catch.
"""

from pydantic import SecretStr

from monopoly.examples.example_bank import ExampleBank
from monopoly.pdf import PdfParser
from monopoly.pipeline import Pipeline
from monopoly.write import generate_name

SAMPLE_PAGE = "01-02-2024\nDATE DESCRIPTION AMOUNT\n12/01 COFFEE SHOP 12.34\n13/01 BOOK STORE 56.78\n"


def test_pipeline_accepts_passwords_and_deferred_safety_check():
    # passwords is unused but still accepted; the caller runs the safety check itself
    parser = PdfParser.from_pages(ExampleBank, [SAMPLE_PAGE])
    pipeline = Pipeline(parser, passwords=[SecretStr("secret")])

    statement = pipeline.extract(safety_check=False)
    transactions = pipeline.transform(statement)

    assert [tx.date for tx in transactions] == ["2024-01-12", "2024-01-13"]


def test_extract_transform_then_generate_name():
    # extract -> transform, with the caller naming the output file itself
    parser = PdfParser.from_pages(ExampleBank, [SAMPLE_PAGE])
    pipeline = Pipeline(parser)

    statement = pipeline.extract(safety_check=False)
    transactions = pipeline.transform(statement)
    filename = generate_name(
        statement=statement,
        format_type="file",
        bank_name=statement.bank_name,
        statement_type=statement.statement_type,
        statement_date=statement.statement_date,
    )

    assert len(transactions) == 2
    assert filename.endswith(".csv")
