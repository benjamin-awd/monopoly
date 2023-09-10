import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks.hsbc import Hsbc


def test_hsbc_extract_unprotected_pdf(hsbc: Hsbc):
    raw_df = hsbc.extract().df
    expected_df = pd.read_csv("tests/fixtures/hsbc/expected.csv", dtype=object)

    assert_frame_equal(raw_df, expected_df)
    raw_df["amount"] = raw_df["amount"].astype("float")

    assert round(raw_df["amount"].sum(), 2) == 1218.2
