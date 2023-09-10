import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks.ocbc import Ocbc


def test_ocbc_extract_unprotected_pdf(ocbc: Ocbc):
    raw_df = ocbc.extract().df

    expected_df = pd.read_csv("tests/fixtures/ocbc/expected.csv", dtype=object)

    assert_frame_equal(raw_df, expected_df)
    raw_df["amount"] = raw_df["amount"].astype("float")

    # check total (excluding cash rebate)
    assert round(raw_df["amount"].sum(), 2) == 703.48
