import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from monopoly.banks.ocbc import OCBC
from monopoly.constants import AMOUNT, DATE, DESCRIPTION
from monopoly.exceptions import UndefinedFilePathError


def test_ocbc_extract_unprotected_pdf(ocbc: OCBC):
    ocbc.file_path = "tests/ocbc_365.pdf"

    raw_df: pd.DataFrame = ocbc.extract()

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


def test_error_raised_if_no_file_path_during_extract():
    with pytest.raises(
        UndefinedFilePathError, match="File path must be defined"
    ):
        pdf = OCBC()
        pdf.extract()
