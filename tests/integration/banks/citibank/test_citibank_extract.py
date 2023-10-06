import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks.citibank import Citibank
from monopoly.helpers.constants import BankStatement


def test_citibank_extract_unprotected_pdf(citibank: Citibank):
    raw_df = citibank.extract().df
    expected_df = pd.read_csv("tests/integration/fixtures/citibank/expected.csv")

    assert_frame_equal(raw_df, expected_df)

    # total excluding $20 cashback
    assert round(raw_df[BankStatement.AMOUNT].sum(), 2) == 1434.07
