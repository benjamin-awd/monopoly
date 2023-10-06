from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.bank import Statement
from monopoly.banks.citibank import Citibank
from monopoly.statement import Transaction


def test_citibank_transform_cross_year(citibank: Citibank, statement: Statement):
    raw_df = pd.DataFrame(
        [
            Transaction("09 JAN", "Shopee Singapore", "31.45"),
            Transaction("12 DEC", "UNIQLO SINGAPORE", "29.80"),
        ]
    )
    statement.statement_date = datetime(2024, 1, 1)
    statement.df = raw_df
    transformed_df = citibank.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2024-01-09", "Shopee Singapore", 31.45),
            Transaction("2023-12-12", "UNIQLO SINGAPORE", 29.80),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)


def test_citibank_transform_within_year(citibank: Citibank, statement: Statement):
    raw_df = pd.DataFrame(
        [
            Transaction("09 JUN", "Shopee Singapore", "31.45"),
            Transaction("12 JUN", "UNIQLO SINGAPORE", "29.80"),
        ]
    )

    statement.statement_date = datetime(2023, 7, 1)
    statement.df = raw_df

    transformed_df = citibank.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2023-06-09", "Shopee Singapore", 31.45),
            Transaction("2023-06-12", "UNIQLO SINGAPORE", 29.80),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)
