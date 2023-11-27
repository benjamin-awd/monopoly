from pathlib import Path

import pytest

from monopoly.pdf import PdfPage
from monopoly.processors import Hsbc, Ocbc, ProcessorBase
from monopoly.statement import Statement


@pytest.mark.parametrize(
    "bank_class, page_content, expected_date",
    [
        (Hsbc, "Statement From 21 JUL 2023 to 20 AUG 2023", "21 Jul 2023"),
        (Ocbc, "01-08-2023 24-08-2023 S$12,345 S$12,345 S$50.00", "01-08-2023"),
    ],
)
def test_statement_date_extraction(
    bank_class: ProcessorBase,
    page_content: list[str],
    expected_date: str,
    statement: Statement,
):
    bank_name = bank_class.statement_config.bank_name

    fixture_directory = Path(__file__).parent / bank_name
    processor: ProcessorBase = bank_class(fixture_directory / "input.pdf")

    statement.statement_config.date_pattern = processor.statement_config.date_pattern
    statement.statement_config.date_format = processor.statement_config.date_format
    statement.pages[0] = PdfPage(raw_text=page_content)

    statement_date = statement.statement_date
    assert statement.source_file_name_date.casefold() == expected_date.casefold()
    assert (
        statement_date.strftime(statement.statement_config.date_format) == expected_date
    )
