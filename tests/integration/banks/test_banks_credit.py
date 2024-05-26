from datetime import datetime
from pathlib import Path

import pytest
from test_utils.skip import skip_if_encrypted
from test_utils.transactions import get_transactions_as_dict, read_transactions_from_csv

from monopoly.banks import Citibank, Dbs, Hsbc, Ocbc, StandardChartered
from monopoly.banks.base import BankBase
from monopoly.handler import StatementHandler
from monopoly.statements import CreditStatement


@skip_if_encrypted
@pytest.mark.parametrize(
    "bank, total_amount, statement_date",
    [
        (Citibank, -1414.07, datetime(2022, 11, 15)),
        (Dbs, -16969.17, datetime(2023, 10, 15)),
        (Hsbc, -1218.2, datetime(2023, 8, 20)),
        (Ocbc, -702.1, datetime(2023, 8, 1)),
        (StandardChartered, -82.45, datetime(2023, 5, 16)),
    ],
)
def test_bank_credit_statements(
    bank: BankBase,
    total_amount: float,
    statement_date: datetime,
):
    bank_name = bank.credit_config.bank_name
    test_directory = Path(__file__).parent / bank_name / "credit"
    statement_handler = StatementHandler(test_directory / "input.pdf")
    statement: CreditStatement = statement_handler.extract()

    # check raw data
    expected_raw_transactions = read_transactions_from_csv(test_directory, "raw.csv")
    raw_transactions_as_dict = get_transactions_as_dict(statement.transactions)
    expected_transaction_total_amount = [
        transaction.amount for transaction in statement.transactions
    ]
    assert expected_raw_transactions == raw_transactions_as_dict
    assert round(sum(expected_transaction_total_amount), 2) == total_amount
    assert statement.statement_date == statement_date
    assert statement.perform_safety_check()

    # check transformed data
    expected_transformed_transactions = read_transactions_from_csv(
        test_directory, "transformed.csv"
    )
    transformed_transactions = statement_handler.transform(
        transactions=statement.transactions,
        statement_date=statement.statement_date,
        transaction_date_order=statement.config.transaction_date_order,
    )
    transformed_transactions_as_dict = get_transactions_as_dict(
        transformed_transactions
    )
    assert expected_transformed_transactions == transformed_transactions_as_dict
