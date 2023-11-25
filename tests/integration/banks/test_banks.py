from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from test_utils.skip import skip_if_encrypted

from monopoly.banks import Citibank, Dbs, Hsbc, Ocbc, StandardChartered
from monopoly.banks.base import BankBase
from monopoly.constants import StatementFields
from monopoly.examples import MonopolyBank
from monopoly.statement import Statement


@skip_if_encrypted
@pytest.mark.parametrize(
    "bank_class, total_amount, statement_date",
    [
        (Citibank, -1414.07, datetime(2022, 11, 15)),
        (Dbs, -16969.17, datetime(2023, 10, 15)),
        (Hsbc, -1218.2, datetime(2023, 7, 21)),
        (Ocbc, -702.1, datetime(2023, 8, 1)),
        (StandardChartered, -82.45, datetime(2023, 5, 16)),
        (MonopolyBank, -702.1, datetime(2023, 7, 1)),
    ],
)
def test_bank_operations(
    bank_class: BankBase,
    total_amount: float,
    statement_date: datetime,
):
    bank_name = bank_class.statement_config.bank_name

    fixture_directory = Path(__file__).parent / bank_name
    bank: BankBase = bank_class(fixture_directory / "input.pdf")
    expected_raw_data = pd.read_csv(fixture_directory / "raw.csv")
    expected_transformed_data = pd.read_csv(fixture_directory / "transformed.csv")

    # Check extracted data is correct
    statement: Statement = bank.extract()

    raw_df = statement.df
    assert_frame_equal(statement.df, expected_raw_data)
    assert round(raw_df[StatementFields.AMOUNT].sum(), 2) == total_amount
    assert statement.statement_date == statement_date
    assert bank._perform_safety_check(statement)

    # Check transformed data is correct
    transformed_df = bank.transform(statement)
    assert_frame_equal(transformed_df, expected_transformed_data)
