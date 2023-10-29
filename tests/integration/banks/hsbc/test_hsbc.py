from datetime import datetime

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from monopoly.banks import Hsbc
from monopoly.constants import StatementFields
from monopoly.statement import Statement


@pytest.fixture(scope="session")
def hsbc_statement(hsbc: Hsbc):
    return hsbc.extract()


def test_hsbc_extract(hsbc_statement: Statement):
    raw_df = hsbc_statement.df
    expected_df = pd.read_csv("tests/integration/fixtures/hsbc/extracted.csv")

    assert_frame_equal(raw_df, expected_df)
    assert round(raw_df[StatementFields.AMOUNT].sum(), 2) == 1218.2
    assert hsbc_statement.statement_date == datetime(2023, 7, 21)


def test_hsbc_transform(hsbc: Hsbc, hsbc_statement):
    expected_df = pd.read_csv("tests/integration/fixtures/hsbc/transformed.csv")
    transformed_df = hsbc.transform(hsbc_statement)

    assert_frame_equal(transformed_df, expected_df)
