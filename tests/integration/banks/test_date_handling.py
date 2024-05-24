from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.config import DateOrder
from monopoly.handler import StatementHandler
from monopoly.statements import Transaction


def test_transform_cross_year(handler: StatementHandler):
    raw_df = pd.DataFrame(
        [
            Transaction("12/01", "FAIRPRICE FINEST", "18.49"),
            Transaction("28/12", "DA PAOLO GASTRONOMIA", "19.69"),
            Transaction("28/11", "KOPITIAM", "5.00"),
        ]
    )
    transformed_df = handler.transform(
        df=raw_df,
        statement_date=datetime(2024, 1, 1),
        transaction_date_order=DateOrder("DMY"),
    )

    expected_data = pd.DataFrame(
        [
            Transaction("2024-01-12", "FAIRPRICE FINEST", 18.49),
            Transaction("2023-12-28", "DA PAOLO GASTRONOMIA", 19.69),
            Transaction("2023-11-28", "KOPITIAM", 5.00),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)


def test_transform_within_year(handler: StatementHandler):
    raw_df = pd.DataFrame(
        [
            Transaction("12/06", "FAIRPRICE FINEST", "18.49"),
            Transaction("12/06", "DA PAOLO GASTRONOMIA", "19.69"),
        ]
    )

    transformed_df = handler.transform(
        df=raw_df,
        statement_date=datetime(2023, 7, 1),
        transaction_date_order=DateOrder("DMY"),
    )

    expected_data = pd.DataFrame(
        [
            Transaction("2023-06-12", "FAIRPRICE FINEST", 18.49),
            Transaction("2023-06-12", "DA PAOLO GASTRONOMIA", 19.69),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)
