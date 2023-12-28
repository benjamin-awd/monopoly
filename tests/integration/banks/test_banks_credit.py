from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from test_utils.skip import skip_if_encrypted

from monopoly.constants import StatementFields
from monopoly.processors import Citibank, Dbs, Hsbc, Ocbc, StandardChartered
from monopoly.processors.base import ProcessorBase
from monopoly.statements import CreditStatement


@skip_if_encrypted
@pytest.mark.parametrize(
    "bank_processor, total_amount, statement_date",
    [
        (Citibank, -1414.07, datetime(2022, 11, 15)),
        (Dbs, -16969.17, datetime(2023, 10, 15)),
        (Hsbc, -1218.2, datetime(2023, 7, 21)),
        (Ocbc, -702.1, datetime(2023, 8, 1)),
        (StandardChartered, -82.45, datetime(2023, 5, 16)),
    ],
)
def test_bank_credit_statements(
    bank_processor: ProcessorBase,
    total_amount: float,
    statement_date: datetime,
):
    processor_name = bank_processor.credit_config.bank_name
    test_directory = Path(__file__).parent / processor_name / "credit"

    processor: ProcessorBase = bank_processor(test_directory / "input.pdf")
    expected_raw_data = pd.read_csv(test_directory / "raw.csv")
    expected_transformed_data = pd.read_csv(test_directory / "transformed.csv")

    # Check extracted data is correct
    statement: CreditStatement = processor.extract()

    raw_df = statement.df
    assert_frame_equal(statement.df, expected_raw_data)
    assert round(raw_df[StatementFields.AMOUNT].sum(), 2) == total_amount
    assert statement.statement_date == statement_date
    assert statement.perform_safety_check()

    # Check transformed data is correct
    transformed_df = processor.transform(statement)
    assert_frame_equal(transformed_df, expected_transformed_data)
