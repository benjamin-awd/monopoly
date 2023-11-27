from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from pandas import DataFrame

from monopoly.processors import ExampleBankProcessor


@pytest.fixture
def mock_generate_name():
    with patch(
        "monopoly.processor.generate_name", return_value="test_file.csv"
    ) as mock:
        yield mock


@pytest.fixture
def mock_to_csv():
    with patch("pandas.DataFrame.to_csv") as mock:
        yield mock


def test_load(statement, mock_generate_name, mock_to_csv):
    df = DataFrame({"Column1": [1, 2, 3], "Column2": ["A", "B", "C"]})
    statement.statement_date = datetime(2023, 1, 1)

    bank_class = ExampleBankProcessor("foo")

    output_path = bank_class.load(df, statement, Path("/output_directory"))

    mock_generate_name.assert_called_once_with(
        file_path="foo",
        format_type="file",
        config=statement.statement_config,
        statement_date=datetime(2023, 1, 1),
    )
    expected = Path("/output_directory/test_file.csv")
    mock_to_csv.assert_called_once_with(expected, index=False)
    assert output_path == expected
