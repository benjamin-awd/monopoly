from pathlib import Path

import pytest

from monopoly.pdf import PdfPage
from monopoly.processors import Hsbc, Ocbc, ProcessorBase
from monopoly.statements import BaseStatement


@pytest.mark.parametrize(
    "bank_class, page_content, expected_date",
    [
        (Hsbc, "Statement From 21 JUL 2023 to 20 AUG 2023", "20 Aug 2023"),
        (Ocbc, "01-08-2023 24-08-2023 S$12,345 S$12,345 S$50.00", "01-08-2023"),
    ],
)
def test_statement_date_extraction(
    bank_class: ProcessorBase,
    page_content: list[str],
    expected_date: str,
    statement: BaseStatement,
):
    bank_name = bank_class.credit_config.bank_name

    fixture_directory = Path(__file__).parent / "banks" / bank_name
    processor: ProcessorBase = bank_class(fixture_directory / "credit/input.pdf")
    statement.statement_config.statement_date_pattern = (
        processor.credit_config.statement_date_pattern
    )
    statement.statement_config.statement_date_format = (
        processor.credit_config.statement_date_format
    )
    statement.pages[0] = PdfPage(raw_text=page_content)

    actual_statement_date = statement.statement_date.strftime(
        statement.statement_config.statement_date_format
    )

    assert actual_statement_date == expected_date
