import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks.citibank import Citibank


def test_citibank_extract_unprotected_pdf(citibank: Citibank):
    raw_df = citibank.extract().df
    expected_df = pd.read_csv("tests/fixtures/citibank/expected.csv", dtype=object)

    assert_frame_equal(raw_df, expected_df)
    raw_df["amount"] = raw_df["amount"].astype("float")

    # total excluding $20 cashback
    assert round(raw_df["amount"].sum(), 2) == 1434.07
