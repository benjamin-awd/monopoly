import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks.ocbc import Ocbc
from monopoly.helpers.constants import BankStatement


def test_ocbc_extract_unprotected_pdf(ocbc: Ocbc):
    raw_df = ocbc.extract().df

    expected_df = pd.read_csv("tests/fixtures/ocbc/expected.csv", dtype=object)

    assert_frame_equal(raw_df, expected_df)
    raw_df[BankStatement.AMOUNT] = raw_df[BankStatement.AMOUNT].astype("float")

    # check total (excluding cash rebate)
    assert round(raw_df[BankStatement.AMOUNT].sum(), 2) == 703.48
