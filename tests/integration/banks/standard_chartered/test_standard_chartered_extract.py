import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks import StandardChartered


def test_standard_chartered_extract_unprotected_pdf(
    standard_chartered: StandardChartered,
):
    raw_df = standard_chartered.extract().df
    expected_df = pd.read_csv(
        "tests/integration/fixtures/standard_chartered/expected.csv"
    )

    assert_frame_equal(raw_df, expected_df)
