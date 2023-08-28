import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from monopoly.banks.ocbc import OCBC
from monopoly.exceptions import UndefinedFilePathError


def test_ocbc_extract_unprotected_pdf(ocbc: OCBC):
    ocbc.file_path = "tests/ocbc/fixtures/input.pdf"
    raw_df = ocbc.extract()
    expected_df = pd.read_csv("tests/ocbc/fixtures/expected.csv", dtype=object)

    assert_frame_equal(raw_df, expected_df)


def test_error_raised_if_no_file_path_during_extract():
    with pytest.raises(UndefinedFilePathError, match="File path must be defined"):
        pdf = OCBC()
        pdf.extract()
