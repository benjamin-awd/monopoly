from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.bank import Statement
from monopoly.banks.ocbc import Ocbc
from monopoly.helpers.constants import AMOUNT, DATE, DESCRIPTION


def test_ocbc_transform_cross_year(ocbc: Ocbc, statement: Statement):
    raw_df = pd.DataFrame(
        [
            {
                DATE: "12/01",
                DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                AMOUNT: "18.49",
            },
            {
                DATE: "28/12",
                DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                AMOUNT: "19.69",
            },
        ]
    )
    statement.statement_date = datetime(2024, 1, 1)
    statement.df = raw_df
    transformed_df = ocbc.transform(statement)

    expected_data = pd.DataFrame(
        [
            {
                DATE: "2024-01-12",
                DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                AMOUNT: 18.49,
            },
            {
                DATE: "2023-12-28",
                DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                AMOUNT: 19.69,
            },
        ]
    )

    assert_frame_equal(transformed_df, expected_data)


def test_ocbc_transform_within_year(ocbc: Ocbc, statement: Statement):
    raw_df = pd.DataFrame(
        [
            {
                DATE: "12/06",
                DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                AMOUNT: "18.49",
            },
            {
                DATE: "12/06",
                DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                AMOUNT: "19.69",
            },
        ]
    )
    statement.statement_date = datetime(2023, 7, 1)
    statement.df = raw_df

    transformed_df = ocbc.transform(statement)

    expected_data = pd.DataFrame(
        [
            {
                DATE: "2023-06-12",
                DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                AMOUNT: 18.49,
            },
            {
                DATE: "2023-06-12",
                DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                AMOUNT: 19.69,
            },
        ]
    )

    assert_frame_equal(transformed_df, expected_data)
