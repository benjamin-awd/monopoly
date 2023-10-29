from datetime import datetime

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from monopoly.banks import Ocbc
from monopoly.constants import StatementFields
from monopoly.statement import Statement


@pytest.fixture(scope="session")
def ocbc_statement(ocbc: Ocbc):
    return ocbc.extract()


def test_ocbc_extract(ocbc_statement: Statement):
    raw_df = ocbc_statement.df
    expected_df = pd.read_csv("tests/integration/fixtures/ocbc/extracted.csv")

    assert_frame_equal(raw_df, expected_df)

    # check total (excluding cash rebate)
    assert round(raw_df[StatementFields.AMOUNT].sum(), 2) == 703.48
    assert ocbc_statement.statement_date == datetime(2023, 8, 1)


def test_ocbc_transform(ocbc: Ocbc, ocbc_statement):
    expected_df = pd.read_csv("tests/integration/fixtures/ocbc/transformed.csv")
    transformed_df = ocbc.transform(ocbc_statement)

    assert_frame_equal(transformed_df, expected_df)
