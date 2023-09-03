from monopoly.banks.hsbc.credit import HsbcRevolution
from monopoly.banks.ocbc.credit import Ocbc365
from monopoly.banks.statement import Statement


def test_hsbc_statement_date_extraction(
    generic_hsbc: HsbcRevolution, statement: Statement
):
    page_content = "Statement From 21 JUL 2023 to 20 AUG 2023"

    statement.config.date_pattern = generic_hsbc.statement_config.date_pattern
    statement.config.statement_date_format = (
        generic_hsbc.statement_config.statement_date_format
    )

    statement.pages[0] = ["foo", page_content]

    expected_date = "21 Jul 2023"
    statement_date = statement.statement_date

    assert statement_date is not None
    assert (
        statement_date.strftime(statement.config.statement_date_format) == expected_date
    )


def test_ocbc_statement_date_extraction(generic_ocbc: Ocbc365, statement: Statement):
    page_content = "01-08-2023 24-08-2023 S$12,345 S$12,345 S$50.00"

    statement.config.date_pattern = generic_ocbc.statement_config.date_pattern
    statement.config.statement_date_format = (
        generic_ocbc.statement_config.statement_date_format
    )

    statement.pages[0] = ["foo", page_content]

    expected_date = "01-08-2023"
    statement_date = statement.statement_date

    assert statement_date is not None
    assert (
        statement_date.strftime(statement.config.statement_date_format) == expected_date
    )
