from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks import StandardChartered
from monopoly.statement import Statement, Transaction


def test_citibank_transform_cross_year(
    standard_chartered: StandardChartered, statement: Statement
):
    raw_df = pd.DataFrame(
        [
            Transaction("31 Dec", "BUS/MRT 253656688 SINGAPORE SG", "3.66"),
            Transaction("01 Jan", "BUS/MRT 254457586 SINGAPORE SG", "1.15"),
        ]
    )
    statement.statement_date = datetime(2024, 1, 1)
    statement.df = raw_df
    transformed_df = standard_chartered.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2023-12-31", "BUS/MRT 253656688 SINGAPORE SG", 3.66),
            Transaction("2024-01-01", "BUS/MRT 254457586 SINGAPORE SG", 1.15),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)


def test_citibank_transform_within_year(
    standard_chartered: StandardChartered, statement: Statement
):
    raw_df = pd.DataFrame(
        [
            Transaction("31 Dec", "BUS/MRT 253656688 SINGAPORE SG", "3.66"),
            Transaction("5 Nov", "BUS/MRT 254457586 SINGAPORE SG", "1.15"),
        ]
    )

    statement.statement_date = datetime(2023, 7, 1)
    statement.df = raw_df

    transformed_df = standard_chartered.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2023-12-31", "BUS/MRT 253656688 SINGAPORE SG", 3.66),
            Transaction("2023-11-05", "BUS/MRT 254457586 SINGAPORE SG", 1.15),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)
