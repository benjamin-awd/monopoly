from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.bank import Statement
from monopoly.banks import Hsbc
from monopoly.statement import Transaction


def test_hsbc_transform_cross_year(hsbc: Hsbc, statement: Statement):
    raw_df = pd.DataFrame(
        [
            Transaction("09 Jan", "Shopee Singapore", "31.45"),
            Transaction("12 Dec", "UNIQLO SINGAPORE", "29.80"),
        ]
    )
    statement.statement_date = datetime(2024, 1, 1)
    statement.df = raw_df
    transformed_df = hsbc.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2024-01-09", "Shopee Singapore", 31.45),
            Transaction("2023-12-12", "UNIQLO SINGAPORE", 29.80),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)


def test_hsbc_transform_within_year(hsbc: Hsbc, statement: Statement):
    raw_df = pd.DataFrame(
        [
            Transaction("09 Jun", "Shopee Singapore", "31.45"),
            Transaction("12 Jun", "UNIQLO SINGAPORE", "29.80"),
        ]
    )

    statement.statement_date = datetime(2023, 7, 1)
    statement.df = raw_df

    transformed_df = hsbc.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2023-06-09", "Shopee Singapore", 31.45),
            Transaction("2023-06-12", "UNIQLO SINGAPORE", 29.80),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)
