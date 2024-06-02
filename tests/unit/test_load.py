from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from monopoly.pipeline import Pipeline
from monopoly.statements import BaseStatement, Transaction


@pytest.fixture
def mock_generate_name():
    with patch("monopoly.pipeline.generate_name", return_value="test_file.csv") as mock:
        yield mock


@pytest.fixture
def mock_file_system():
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        with patch("csv.writer", autospec=True) as mock_writer:
            mock_instance = mock_writer.return_value
            mock_instance.writerow = MagicMock()
            yield mock_open, mock_instance


@pytest.mark.usefixtures("mock_generate_name")
def test_load(
    credit_statement: BaseStatement,
    mock_file_system,
):
    mock_open, mock_csv_writer = mock_file_system

    transactions = [
        Transaction(transaction_date="2023-01-01", description="foo", amount=100.0),
        Transaction(transaction_date="2023-01-01", description="bar", amount=123.12),
    ]

    credit_statement.statement_date = datetime(2023, 1, 1)

    output_path = Pipeline.load(
        transactions=transactions,
        statement=credit_statement,
        output_directory=Path("/output_directory"),
    )

    expected = Path("/output_directory/test_file.csv")
    mock_open.assert_called_once_with(expected, mode="w", encoding="utf8")
    expected_calls = [
        call.writerow(["date", "description", "amount"]),
        call.writerow(["2023-01-01", "foo", -100.0]),
        call.writerow(["2023-01-01", "bar", -123.12]),
    ]

    mock_csv_writer.writerow.assert_has_calls(expected_calls)
    assert output_path == expected
