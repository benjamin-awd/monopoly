from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from test_utils.skip import skip_if_encrypted

from monopoly.banks import BankBase, Dbs, Ocbc
from monopoly.constants import StatementFields
from monopoly.handler import StatementHandler
from monopoly.statements import DebitStatement


@skip_if_encrypted
@pytest.mark.parametrize(
    "bank, expected_debit_sum, expected_credit_sum, statement_date",
    [
        (Dbs, 2222.68, 1302.88, datetime(2023, 10, 31)),
        (Ocbc, 6630.79, 5049.55, datetime(2023, 10, 1)),
    ],
)
def test_bank_debit_statements(
    bank: BankBase,
    expected_debit_sum: float,
    expected_credit_sum: float,
    statement_date: datetime,
):
    bank_name = bank.debit_config.bank_name
    test_directory = Path(__file__).parent / bank_name / "debit"
    statement_handler = StatementHandler(test_directory / "input.pdf")
    statement: DebitStatement = statement_handler.extract()

    # check raw data
    expected_raw_data = pd.read_csv(test_directory / "raw.csv")
    df = statement.df
    amount = StatementFields.AMOUNT

    debit_sum = round(abs(df[df[amount] > 0][amount].sum()), 2)
    credit_sum = round(abs(df[df[amount] < 0][amount].sum()), 2)

    assert_frame_equal(statement.df, expected_raw_data)
    assert debit_sum == expected_debit_sum
    assert credit_sum == expected_credit_sum
    assert statement.statement_date == statement_date
    assert statement.perform_safety_check()

    # check transformed data
    expected_transformed_data = pd.read_csv(test_directory / "transformed.csv")
    transformed_df = statement_handler.transform(
        df=df,
        statement_date=statement.statement_date,
        transaction_date_order=statement.config.transaction_date_order,
    )
    assert_frame_equal(transformed_df, expected_transformed_data)
