from datetime import date, datetime
from pathlib import Path

import pytest
from test_utils.transactions import get_transactions_as_dict, read_pages, read_transactions_from_csv

from monopoly.banks import Citibank, Dbs, Hsbc, Maybank, Ocbc, StandardChartered, Trust
from monopoly.banks.base import BankBase
from monopoly.pdf import PdfParser
from monopoly.pipeline import Pipeline
from monopoly.statements import CreditStatement, PaymentSummary

# These run against committed, synthetic, plain-text fixtures (page_NN.txt) - no
# real statements, no encryption. Totals/dates below are the synthetic values.
test_cases = [
    (Citibank, -310.8, datetime(2022, 3, 12)),
    (Dbs, -550.0, datetime(2023, 11, 20)),
    (Hsbc, -575.94, datetime(2024, 9, 24)),
    (Maybank, -1209.5, datetime(2024, 11, 8)),
    (Ocbc, -210.0, datetime(2023, 9, 1)),
    (StandardChartered, -194.75, datetime(2024, 6, 18)),
    (Trust, -27.0, datetime(2025, 3, 15)),
]

# expected payment summary per bank that configures one, keyed by bank name
expected_payment_summaries = {
    "citibank": PaymentSummary(date(2022, 4, 6), 310.8, 50.00),
    "dbs": PaymentSummary(date(2023, 12, 15), 550.0, 50.00),
    # HSBC prints no payment due date, so it stays None
    "hsbc": PaymentSummary(None, 575.94, 50.00),
    "ocbc": PaymentSummary(date(2023, 9, 22), 210.0, 50.00),
    "standard_chartered": PaymentSummary(date(2024, 7, 10), 194.75, 50.00),
    "trust": PaymentSummary(date(2025, 4, 5), 27.0, 25.00),
}


@pytest.mark.parametrize(
    "bank, total_amount, statement_date",
    test_cases,
)
def test_bank_credit_statements(
    bank: BankBase,
    total_amount: float,
    statement_date: datetime,
):
    test_directory = Path(__file__).parent / bank.name / "credit"

    parser = PdfParser.from_pages(bank, read_pages(test_directory))
    pipeline = Pipeline(parser)
    statement: CreditStatement = pipeline.extract()

    # check raw data
    expected_raw_transactions = read_transactions_from_csv(test_directory, "raw.csv")
    raw_transactions_as_dict = get_transactions_as_dict(statement.transactions)
    expected_transaction_total_amount = [transaction.amount for transaction in statement.transactions]
    assert expected_raw_transactions == raw_transactions_as_dict
    assert round(sum(expected_transaction_total_amount), 2) == total_amount
    assert statement.statement_date == statement_date

    # check transformed data
    expected_transformed_transactions = read_transactions_from_csv(test_directory, "transformed.csv")
    transformed_transactions = pipeline.transform(statement)
    transformed_transactions_as_dict = get_transactions_as_dict(transformed_transactions)
    assert expected_transformed_transactions == transformed_transactions_as_dict

    # check the extracted payment summary, for banks that configure one
    if expected_summary := expected_payment_summaries.get(bank.name):
        assert statement.payment_summary == expected_summary
