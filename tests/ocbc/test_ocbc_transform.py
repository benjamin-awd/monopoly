from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.bank import Statement
from monopoly.banks.ocbc import Ocbc
from monopoly.helpers.constants import BankStatement


def test_ocbc_transform_cross_year(ocbc: Ocbc, statement: Statement):
    raw_df = pd.DataFrame(
        [
            {
                BankStatement.DATE: "12/01",
                BankStatement.DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                BankStatement.AMOUNT: "18.49",
            },
            {
                BankStatement.DATE: "28/12",
                BankStatement.DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                BankStatement.AMOUNT: "19.69",
            },
        ]
    )
    statement.statement_date = datetime(2024, 1, 1)
    statement.df = raw_df
    transformed_df = ocbc.transform(statement)

    expected_data = pd.DataFrame(
        [
            {
                BankStatement.DATE: "2024-01-12",
                BankStatement.DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                BankStatement.AMOUNT: 18.49,
            },
            {
                BankStatement.DATE: "2023-12-28",
                BankStatement.DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                BankStatement.AMOUNT: 19.69,
            },
        ]
    )

    assert_frame_equal(transformed_df, expected_data)


def test_ocbc_transform_within_year(ocbc: Ocbc, statement: Statement):
    raw_df = pd.DataFrame(
        [
            {
                BankStatement.DATE: "12/06",
                BankStatement.DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                BankStatement.AMOUNT: "18.49",
            },
            {
                BankStatement.DATE: "12/06",
                BankStatement.DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                BankStatement.AMOUNT: "19.69",
            },
        ]
    )
    statement.statement_date = datetime(2023, 7, 1)
    statement.df = raw_df

    transformed_df = ocbc.transform(statement)

    expected_data = pd.DataFrame(
        [
            {
                BankStatement.DATE: "2023-06-12",
                BankStatement.DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                BankStatement.AMOUNT: 18.49,
            },
            {
                BankStatement.DATE: "2023-06-12",
                BankStatement.DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                BankStatement.AMOUNT: 19.69,
            },
        ]
    )

    assert_frame_equal(transformed_df, expected_data)
