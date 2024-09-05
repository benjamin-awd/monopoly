from datetime import datetime
from pathlib import Path

import pytest
from test_utils.skip import skip_if_encrypted
from test_utils.transactions import get_transactions_as_dict, read_transactions_from_csv

from monopoly.banks import BankBase, Dbs, Maybank, Ocbc
from monopoly.pdf import PdfParser
from monopoly.pipeline import Pipeline
from monopoly.statements import DebitStatement

test_cases = [
    (Dbs, 2222.68, 1302.88, datetime(2023, 10, 31)),
    (Maybank, 5275.61, 4093.7, datetime(2023, 8, 31)),
    (Ocbc, 6630.79, 5049.55, datetime(2023, 10, 31)),
]


@pytest.fixture
def no_banks(monkeypatch):
    monkeypatch.setattr("monopoly.banks.banks", [])


@skip_if_encrypted
@pytest.mark.parametrize(
    "bank, expected_debit_sum, expected_credit_sum, statement_date",
    test_cases,
)
@pytest.mark.usefixtures("no_banks")
def test_bank_debit_statements(
    bank: BankBase,
    expected_debit_sum: float,
    expected_credit_sum: float,
    statement_date: datetime,
):
    bank_name = bank.debit_config.bank_name
    test_directory = Path(__file__).parent / bank_name / "debit"
    pipeline = Pipeline(test_directory / "input.pdf")

    parser = PdfParser(bank, pipeline.document)
    pages = parser.get_pages()
    statement: DebitStatement = pipeline.extract(pages)

    # check raw data
    expected_raw_transactions = read_transactions_from_csv(test_directory, "raw.csv")
    raw_transactions_as_dict = get_transactions_as_dict(statement.transactions)

    debit_amounts = [
        transaction.amount
        for transaction in statement.transactions
        if transaction.amount > 0
    ]
    credit_amounts = [
        transaction.amount
        for transaction in statement.transactions
        if transaction.amount < 0
    ]

    debit_sum = round(abs(sum(debit_amounts)), 2)
    credit_sum = round(abs(sum(credit_amounts)), 2)

    assert expected_raw_transactions == raw_transactions_as_dict
    assert debit_sum == expected_debit_sum
    assert credit_sum == expected_credit_sum
    assert statement.statement_date == statement_date
    assert statement.perform_safety_check()

    # check transformed data
    expected_transformed_transactions = read_transactions_from_csv(
        test_directory, "transformed.csv"
    )
    transformed_transactions = pipeline.transform(statement)
    transformed_transactions_as_dict = get_transactions_as_dict(
        transformed_transactions
    )
    assert expected_transformed_transactions == transformed_transactions_as_dict
