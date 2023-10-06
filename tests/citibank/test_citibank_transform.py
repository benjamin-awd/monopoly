from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.bank import Statement
from monopoly.banks.citibank import Citibank
from monopoly.helpers.constants import BankStatement


def test_citibank_transform_cross_year(citibank: Citibank, statement: Statement):
    raw_df = pd.DataFrame(
        [
            {
                BankStatement.DATE: "09 JAN",
                BankStatement.DESCRIPTION: "Shopee Singapore SINGAPORE SG",
                BankStatement.AMOUNT: "31.45",
            },
            {
                BankStatement.DATE: "12 DEC",
                BankStatement.DESCRIPTION: "UNIQLO SINGAPORE PTE. SINGAPORE SG",
                BankStatement.AMOUNT: "29.80",
            },
        ]
    )
    statement.statement_date = datetime(2024, 1, 1)
    statement.df = raw_df
    transformed_df = citibank.transform(statement)

    expected_data = pd.DataFrame(
        [
            {
                BankStatement.DATE: "2024-01-09",
                BankStatement.DESCRIPTION: "Shopee Singapore SINGAPORE SG",
                BankStatement.AMOUNT: 31.45,
            },
            {
                BankStatement.DATE: "2023-12-12",
                BankStatement.DESCRIPTION: "UNIQLO SINGAPORE PTE. SINGAPORE SG",
                BankStatement.AMOUNT: 29.80,
            },
        ]
    )

    assert_frame_equal(transformed_df, expected_data)


def test_citibank_transform_within_year(citibank: Citibank, statement: Statement):
    raw_df = pd.DataFrame(
        [
            {
                BankStatement.DATE: "09 JUN",
                BankStatement.DESCRIPTION: "Shopee Singapore SINGAPORE SG",
                BankStatement.AMOUNT: "31.45",
            },
            {
                BankStatement.DATE: "12 JUN",
                BankStatement.DESCRIPTION: "UNIQLO SINGAPORE PTE. SINGAPORE SG",
                BankStatement.AMOUNT: "29.80",
            },
        ]
    )

    statement.statement_date = datetime(2023, 7, 1)
    statement.df = raw_df

    transformed_df = citibank.transform(statement)

    expected_data = pd.DataFrame(
        [
            {
                BankStatement.DATE: "2023-06-09",
                BankStatement.DESCRIPTION: "Shopee Singapore SINGAPORE SG",
                BankStatement.AMOUNT: 31.45,
            },
            {
                BankStatement.DATE: "2023-06-12",
                BankStatement.DESCRIPTION: "UNIQLO SINGAPORE PTE. SINGAPORE SG",
                BankStatement.AMOUNT: 29.80,
            },
        ]
    )

    assert_frame_equal(transformed_df, expected_data)
