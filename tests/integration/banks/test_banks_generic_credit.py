from datetime import datetime
from pathlib import Path

import pytest
from test_utils.transactions import read_pages

from monopoly.generic import GenericBank
from monopoly.pdf import PdfParser
from monopoly.pipeline import Pipeline
from monopoly.statements import CreditStatement

# The generic handler auto-detects the transaction/date pattern instead of using
# a bank config, so it can extract a different row set (and sign/date) than the
# specific handler - e.g. it does not apply OCBC's prev-balance handling. These
# expectations are what the generic handler produces on the synthetic fixtures,
# so we assert totals + statement date rather than the specific raw.csv rows.
# HSBC and Trust are excluded (multi-column / non-generic layouts).
test_cases = [
    ("citibank", -310.8, datetime(2022, 3, 12)),
    ("dbs", -550.0, datetime(2023, 11, 20)),
    ("maybank", -1209.5, datetime(2024, 11, 8)),
    ("ocbc", 710.0, datetime(2023, 9, 1)),
    ("standard_chartered", -194.75, datetime(2024, 6, 18)),
    ("uob", -382.45, datetime(2025, 2, 28)),
]


@pytest.mark.parametrize(
    "bank_name, total_amount, statement_date",
    test_cases,
)
def test_bank_credit_statements(bank_name: str, total_amount: float, statement_date: datetime):
    test_directory = Path(__file__).parent / bank_name / "credit"

    parser = PdfParser.from_pages(GenericBank, read_pages(test_directory))
    pipeline = Pipeline(parser)
    statement: CreditStatement = pipeline.extract()

    assert statement.transactions
    assert round(sum(t.amount for t in statement.transactions), 2) == total_amount
    assert statement.statement_date == statement_date

    # transform must succeed end-to-end (ISO 8601 dates)
    transformed = pipeline.transform(statement)
    assert len(transformed) == len(statement.transactions)
