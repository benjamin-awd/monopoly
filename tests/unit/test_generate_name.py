from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from monopoly.write import generate_name


@pytest.fixture
def mock_generate_hash():
    with patch("monopoly.write.generate_hash") as mock:
        mock.return_value = "b960bf1e"
        yield mock


@pytest.mark.usefixtures("mock_generate_hash")
def test_generate_name():
    statement = MagicMock()
    bank_name = "hsbc"
    statement_date = datetime(2023, 6, 15)
    statement_type = "credit"

    expected_filename = "hsbc-credit-2023-06-b960bf1e.csv"
    # Test for format_type="file"
    filename = generate_name(
        statement=statement,
        format_type="file",
        bank_name=bank_name,
        statement_type=statement_type,
        statement_date=statement_date,
    )
    assert filename == expected_filename

    # Test for format_type="blob"
    filename = generate_name(
        statement=statement,
        format_type="blob",
        bank_name=bank_name,
        statement_type=statement_type,
        statement_date=statement_date,
    )
    assert filename == f"bank_name=hsbc/account_type=credit/statement_date=2023-06-15/{expected_filename}"

    # Test for invalid format_type
    with pytest.raises(ValueError, match="Invalid format_type"):
        generate_name(
            statement=statement,
            format_type="invalid_format",
            bank_name=bank_name,
            statement_type=statement_type,
            statement_date=statement_date,
        )
