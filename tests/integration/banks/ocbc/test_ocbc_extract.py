import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks import Ocbc
from monopoly.constants import StatementFields


def test_ocbc_extract_unprotected_pdf(ocbc: Ocbc):
    raw_df = ocbc.extract().df

    expected_df = pd.read_csv("tests/integration/fixtures/ocbc/expected.csv")

    assert_frame_equal(raw_df, expected_df)

    # check total (excluding cash rebate)
    assert round(raw_df[StatementFields.AMOUNT].sum(), 2) == 703.48
