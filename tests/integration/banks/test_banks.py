from datetime import datetime

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from monopoly.banks import Citibank, Dbs, Hsbc, Ocbc, StandardChartered
from monopoly.banks.base import BankBase
from monopoly.constants import StatementFields
from monopoly.statement import Statement


@pytest.mark.parametrize(
    "bank_class, total_amount, statement_date",
    [
        (Citibank, 1434.07, datetime(2022, 11, 15)),
        (Dbs, 16969.17, datetime(2023, 10, 15)),
        (Hsbc, 1218.2, datetime(2023, 7, 21)),
        (Ocbc, 703.48, datetime(2023, 8, 1)),
        (StandardChartered, 82.45, datetime(2023, 5, 16)),
    ],
)
def test_bank_operations(bank_class: BankBase, total_amount, statement_date):
    bank_name = bank_class.statement_config.bank_name
    bank: BankBase = bank_class(
        file_path=f"tests/integration/fixtures/{bank_name}/input.pdf"
    )
    raw_data = pd.read_csv(f"tests/integration/fixtures/{bank_name}/raw.csv")
    transformed_data = pd.read_csv(
        f"tests/integration/fixtures/{bank_name}/transformed.csv"
    )

    # Check extracted data is correct
    statement: Statement = bank.extract()
    raw_df = statement.df
    assert_frame_equal(statement.df, raw_data)
    assert round(raw_df[StatementFields.AMOUNT].sum(), 2) == total_amount
    assert statement.statement_date == statement_date

    # Check transformed data is correct
    transformed_df = bank.transform(statement)
    assert_frame_equal(transformed_df, transformed_data)
