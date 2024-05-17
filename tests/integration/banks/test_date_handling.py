from datetime import datetime
from unittest.mock import PropertyMock

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.processor import StatementProcessor
from monopoly.statements import BaseStatement, Transaction


def test_transform_cross_year(processor: StatementProcessor, statement: BaseStatement):
    raw_df = pd.DataFrame(
        [
            Transaction("12/01", "FAIRPRICE FINEST", "18.49"),
            Transaction("28/12", "DA PAOLO GASTRONOMIA", "19.69"),
            Transaction("28/11", "KOPITIAM", "5.00"),
        ]
    )
    type(statement).statement_date = PropertyMock(return_value=(datetime(2024, 1, 1)))
    statement.df = raw_df
    transformed_df = processor.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2024-01-12", "FAIRPRICE FINEST", 18.49),
            Transaction("2023-12-28", "DA PAOLO GASTRONOMIA", 19.69),
            Transaction("2023-11-28", "KOPITIAM", 5.00),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)


def test_transform_within_year(processor: StatementProcessor, statement: BaseStatement):
    raw_df = pd.DataFrame(
        [
            Transaction("12/06", "FAIRPRICE FINEST", "18.49"),
            Transaction("12/06", "DA PAOLO GASTRONOMIA", "19.69"),
        ]
    )
    type(statement).statement_date = PropertyMock(return_value=(datetime(2023, 7, 1)))
    statement.df = raw_df

    transformed_df = processor.transform(statement)

    expected_data = pd.DataFrame(
        [
            Transaction("2023-06-12", "FAIRPRICE FINEST", 18.49),
            Transaction("2023-06-12", "DA PAOLO GASTRONOMIA", 19.69),
        ]
    )

    assert_frame_equal(transformed_df, expected_data)
