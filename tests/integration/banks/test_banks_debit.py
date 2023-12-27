from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from test_utils.skip import skip_if_encrypted

from monopoly.constants import StatementFields
from monopoly.debit_statement import DebitStatement
from monopoly.processors import Dbs, Ocbc
from monopoly.processors.base import ProcessorBase


@skip_if_encrypted
@pytest.mark.parametrize(
    "bank_processor, expected_debit_sum, expected_credit_sum, statement_date",
    [
        (Dbs, 2222.68, 1302.88, datetime(2023, 10, 31)),
        (Ocbc, 6630.79, 5049.55, datetime(2023, 10, 1)),
    ],
)
def test_bank_debit_statements(
    bank_processor: ProcessorBase,
    expected_debit_sum: float,
    expected_credit_sum: float,
    statement_date: datetime,
):
    processor_name = bank_processor.debit_config.bank_name
    test_directory = Path(__file__).parent / processor_name / "debit"

    processor: ProcessorBase = bank_processor(test_directory / "input.pdf")
    expected_raw_data = pd.read_csv(test_directory / "raw.csv")
    expected_transformed_data = pd.read_csv(test_directory / "transformed.csv")

    # Check extracted data is correct
    statement: DebitStatement = processor.extract()

    df = statement.df
    amount = StatementFields.AMOUNT

    debit_sum = round(abs(df[df[amount] > 0][amount].sum()), 2)
    credit_sum = round(abs(df[df[amount] < 0][amount].sum()), 2)

    assert_frame_equal(statement.df, expected_raw_data)
    assert debit_sum == expected_debit_sum
    assert credit_sum == expected_credit_sum
    assert statement.statement_date == statement_date
    assert statement.perform_safety_check()

    # Check transformed data is correct
    transformed_df = processor.transform(statement)
    assert_frame_equal(transformed_df, expected_transformed_data)
