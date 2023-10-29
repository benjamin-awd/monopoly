from datetime import datetime

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from monopoly.banks import Citibank
from monopoly.constants import StatementFields
from monopoly.statement import Statement


@pytest.fixture(scope="session")
def citibank_statement(citibank: Citibank):
    return citibank.extract()


def test_citibank_extract(citibank_statement: Statement):
    raw_df = citibank_statement.df
    expected_df = pd.read_csv("tests/integration/fixtures/citibank/extracted.csv")

    assert_frame_equal(raw_df, expected_df)

    # total excluding $20 cashback
    assert round(raw_df[StatementFields.AMOUNT].sum(), 2) == 1434.07

    assert citibank_statement.statement_date == datetime(2022, 11, 15)


def test_citibank_transform(citibank: Citibank, citibank_statement):
    expected_df = pd.read_csv("tests/integration/fixtures/citibank/transformed.csv")
    transformed_df = citibank.transform(citibank_statement)

    assert_frame_equal(transformed_df, expected_df)
