from datetime import datetime

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from monopoly.banks import Dbs
from monopoly.constants import StatementFields
from monopoly.statement import Statement


@pytest.fixture(scope="session")
def dbs_statement(dbs: Dbs):
    return dbs.extract()


def test_dbs_extract(dbs_statement: Statement):
    raw_df = dbs_statement.df
    expected_df = pd.read_csv("tests/integration/fixtures/dbs/extracted.csv")

    assert_frame_equal(raw_df, expected_df)
    assert raw_df[StatementFields.AMOUNT].sum() == 16969.17
    assert dbs_statement.statement_date == datetime(2023, 10, 15)


def test_dbs_transform(dbs: Dbs, dbs_statement):
    expected_df = pd.read_csv("tests/integration/fixtures/dbs/transformed.csv")
    transformed_df = dbs.transform(dbs_statement)

    assert_frame_equal(transformed_df, expected_df)
