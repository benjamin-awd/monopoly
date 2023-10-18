import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks import Hsbc
from monopoly.constants import StatementFields


def test_hsbc_extract_unprotected_pdf(hsbc: Hsbc):
    pages = hsbc.get_pages()
    raw_df = hsbc.extract(pages).df
    expected_df = pd.read_csv("tests/integration/fixtures/hsbc/expected.csv")

    assert_frame_equal(raw_df, expected_df)

    assert round(raw_df[StatementFields.AMOUNT].sum(), 2) == 1218.2
