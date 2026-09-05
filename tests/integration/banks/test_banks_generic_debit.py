from datetime import datetime
from pathlib import Path

import pytest
from test_utils.transactions import read_pages

from monopoly.generic import GenericBank
from monopoly.pdf import PdfParser
from monopoly.pipeline import Pipeline
from monopoly.statements import DebitStatement

# What the generic handler produces on the synthetic debit fixtures. The generic
# handler may resolve a different statement_date than the specific config (e.g.
# OCBC: period-start vs statement-end), so these are the generic values.
test_cases = [
    ("dbs", 1653.65, 396.65, datetime(2024, 11, 30)),
    ("maybank", 525.25, 464.0, datetime(2023, 8, 31)),
    ("ocbc", 3670.25, 1596.1, datetime(2024, 9, 1)),
]


@pytest.mark.parametrize(
    "bank_name, expected_debit_sum, expected_credit_sum, statement_date",
    test_cases,
)
def test_bank_debit_statements(
    bank_name: str,
    expected_debit_sum: float,
    expected_credit_sum: float,
    statement_date: datetime,
):
    test_directory = Path(__file__).parent / bank_name / "debit"

    parser = PdfParser.from_pages(GenericBank, read_pages(test_directory))
    pipeline = Pipeline(parser)
    statement: DebitStatement = pipeline.extract()

    debit_amounts = [t.amount for t in statement.transactions if t.amount > 0]
    credit_amounts = [t.amount for t in statement.transactions if t.amount < 0]

    assert round(abs(sum(debit_amounts)), 2) == expected_debit_sum
    assert round(abs(sum(credit_amounts)), 2) == expected_credit_sum
    assert statement.statement_date == statement_date
    assert statement.perform_safety_check()
