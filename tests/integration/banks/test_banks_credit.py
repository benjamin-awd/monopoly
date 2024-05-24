from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from test_utils.skip import skip_if_encrypted

from monopoly.banks import Citibank, Dbs, Hsbc, Ocbc, StandardChartered
from monopoly.banks.base import BankBase
from monopoly.constants import StatementFields
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
    expected_raw_data = pd.read_csv(test_directory / "raw.csv")
    df = statement.df
    assert_frame_equal(df, expected_raw_data)
    assert round(df[StatementFields.AMOUNT].sum(), 2) == total_amount
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
