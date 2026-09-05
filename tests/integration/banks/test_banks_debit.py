import json
from datetime import datetime
from pathlib import Path

import pytest
from test_utils.transactions import get_transactions_as_dict, read_pages, read_transactions_from_csv

from monopoly.banks import BankBase, BankOfAmerica, Dbs, Maybank, Ocbc, Uob, ZurcherKantonalBank
from monopoly.pdf import PdfParser
from monopoly.pipeline import Pipeline
from monopoly.serialize import statement_to_dict
from monopoly.statements import DebitStatement

# Synthetic, plain-text fixtures (page_NN.txt) - no real statements, no encryption.
test_cases = [
    (BankOfAmerica, 2770.15, 954.55, datetime(2023, 7, 25)),
    (Dbs, 1653.65, 396.65, datetime(2024, 11, 30)),
    (Maybank, 525.25, 464.0, datetime(2023, 8, 31)),
    (Ocbc, 3670.25, 1596.1, datetime(2024, 9, 30)),
    (Uob, 3320.45, 398.8, datetime(2025, 3, 31)),
    (ZurcherKantonalBank, 6313.75, 4062.75, datetime(2025, 9, 5)),
]


@pytest.mark.parametrize(
    "bank, expected_debit_sum, expected_credit_sum, statement_date",
    test_cases,
)
def test_bank_debit_statements(
    bank: BankBase,
    expected_debit_sum: float,
    expected_credit_sum: float,
    statement_date: datetime,
):
    test_directory = Path(__file__).parent / bank.name / "debit"

    parser = PdfParser.from_pages(bank, read_pages(test_directory))
    pipeline = Pipeline(parser)
    statement: DebitStatement = pipeline.extract()

    # check raw data
    expected_raw_transactions = read_transactions_from_csv(test_directory, "raw.csv")
    raw_transactions_as_dict = get_transactions_as_dict(statement.transactions)

    debit_amounts = [transaction.amount for transaction in statement.transactions if transaction.amount > 0]
    credit_amounts = [transaction.amount for transaction in statement.transactions if transaction.amount < 0]

    debit_sum = round(abs(sum(debit_amounts)), 2)
    credit_sum = round(abs(sum(credit_amounts)), 2)

    assert expected_raw_transactions == raw_transactions_as_dict
    assert debit_sum == expected_debit_sum
    assert credit_sum == expected_credit_sum
    assert statement.statement_date == statement_date
    # some banks (BoA, ZKB) print no reconcilable total and set safety_check=False
    if statement.config.safety_check:
        assert statement.perform_safety_check()

    # check transformed data
    expected_transformed_transactions = read_transactions_from_csv(test_directory, "transformed.csv")
    transformed_transactions = pipeline.transform(statement)
    transformed_transactions_as_dict = get_transactions_as_dict(transformed_transactions)
    assert expected_transformed_transactions == transformed_transactions_as_dict

    # the fixture pins the exact `--format json` envelope the CLI would emit
    expected_envelope = json.loads((test_directory / "expected.json").read_text())
    assert statement_to_dict(statement, transformed_transactions) == expected_envelope
