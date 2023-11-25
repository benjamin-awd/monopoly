from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from pandas import DataFrame

from monopoly.banks import ExampleBank


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

    bank_class = ExampleBank("foo")

    output_path = bank_class.load(df, statement, Path("/output_directory"))

    mock_generate_name.assert_called_once_with(
        "file", statement.statement_config, datetime(2023, 1, 1)
    )
    mock_to_csv.assert_called_once_with("/output_directory/test_file.csv", index=False)
    assert output_path == "/output_directory/test_file.csv"
