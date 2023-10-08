import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks import Hsbc
from monopoly.helpers.constants import BankStatement


def test_hsbc_extract_unprotected_pdf(hsbc: Hsbc):
    raw_df = hsbc.extract().df
    expected_df = pd.read_csv("tests/integration/fixtures/hsbc/expected.csv")

    assert_frame_equal(raw_df, expected_df)

    assert round(raw_df[BankStatement.AMOUNT].sum(), 2) == 1218.2
