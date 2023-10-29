from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks import Ocbc
from monopoly.statement import Statement, Transaction


def test_transform_cross_year(ocbc: Ocbc, statement: Statement):
    raw_df = pd.DataFrame(
        [
            Transaction("12/01", "FAIRPRICE FINEST", "18.49"),
            Transaction("28/12", "DA PAOLO GASTRONOMIA", "19.69"),
        ]
    )
    statement.statement_date = datetime(2024, 1, 1)
    statement.df = raw_df
    transformed_df = ocbc.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2024-01-12", "FAIRPRICE FINEST", 18.49),
            Transaction("2023-12-28", "DA PAOLO GASTRONOMIA", 19.69),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)


def test_transform_within_year(ocbc: Ocbc, statement: Statement):
    raw_df = pd.DataFrame(
        [
            Transaction("12/06", "FAIRPRICE FINEST", "18.49"),
            Transaction("12/06", "DA PAOLO GASTRONOMIA", "19.69"),
        ]
    )
    statement.statement_date = datetime(2023, 7, 1)
    statement.df = raw_df

    transformed_df = ocbc.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2023-06-12", "FAIRPRICE FINEST", 18.49),
            Transaction("2023-06-12", "DA PAOLO GASTRONOMIA", 19.69),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)
