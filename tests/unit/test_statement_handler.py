from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pandas import DataFrame

from monopoly.constants import AccountType
from monopoly.handler import StatementHandler
from monopoly.statements import BaseStatement


@pytest.fixture
def mock_generate_name():
    with patch("monopoly.handler.generate_name", return_value="test_file.csv") as mock:
        yield mock


@pytest.fixture
def mock_to_csv():
    with patch("pandas.DataFrame.to_csv") as mock:
        yield mock


def test_load(
    credit_statement: BaseStatement,
    mock_generate_name,
    mock_to_csv,
):
    mock_statement_handler = MagicMock()
    mock_statement_handler.parser.document = "foo"
    df = DataFrame({"Column1": [1, 2, 3], "Column2": ["A", "B", "C"]})
    credit_statement.statement_date = datetime(2023, 1, 1)

    output_path = StatementHandler.load(
        mock_statement_handler,
        df=df,
        statement=credit_statement,
        output_directory=Path("/output_directory"),
    )

    mock_generate_name.assert_called_once_with(
        document="foo",
        format_type="file",
        statement_config=credit_statement.config,
        statement_type=AccountType.CREDIT,
        statement_date=datetime(2023, 1, 1),
    )
    expected = Path("/output_directory/test_file.csv")
    mock_to_csv.assert_called_once_with(expected, index=False)
    assert output_path == expected
