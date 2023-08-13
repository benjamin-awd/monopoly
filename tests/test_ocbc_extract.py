import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks.ocbc import OCBC
from monopoly.constants import AMOUNT, DATE, DESCRIPTION


def test_ocbc_extract_unprotected_pdf():
    pdf = OCBC(file_path="tests/ocbc_365.pdf")
    raw_df: pd.DataFrame = pdf.extract()

    expected_df = pd.DataFrame(
        [
            {
                DATE: "12/06",
                DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                AMOUNT: "18.49",
            },
            {
                DATE: "12/06",
                DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                AMOUNT: "19.69",
            },
        ]
    )

    assert_frame_equal(raw_df, expected_df)
