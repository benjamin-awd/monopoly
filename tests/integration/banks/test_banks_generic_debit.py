from datetime import datetime
from pathlib import Path

import pytest
from test_utils.skip import skip_if_encrypted
from test_utils.transactions import get_transactions_as_dict, read_transactions_from_csv

from monopoly.banks import BankBase, Dbs, Maybank, Ocbc
from monopoly.generic import GenericBank
from monopoly.pdf import PdfDocument, PdfParser
from monopoly.pipeline import Pipeline
from monopoly.statements import DebitStatement

test_cases = [
    (Dbs, 2222.68, 1302.88, datetime(2023, 10, 31)),
    (Maybank, 5275.61, 4093.7, datetime(2023, 8, 31)),
    (Ocbc, 6630.79, 5049.55, datetime(2023, 10, 31)),
]


@skip_if_encrypted
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

    document = PdfDocument(test_directory / "input.pdf")
    parser = PdfParser(bank, document)
    parser.bank = GenericBank
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
    assert statement.perform_safety_check()

    # check transformed data
    expected_transformed_transactions = read_transactions_from_csv(test_directory, "transformed.csv")
    transformed_transactions = pipeline.transform(statement)
    transformed_transactions_as_dict = get_transactions_as_dict(transformed_transactions)
    assert expected_transformed_transactions == transformed_transactions_as_dict
