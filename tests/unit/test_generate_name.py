from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from monopoly.statements import Transaction
from monopoly.write import generate_hash, generate_name


@pytest.fixture
def mock_generate_hash():
    with patch("monopoly.write.generate_hash") as mock:
        mock.return_value = "b960bf1e"
        yield mock


def test_generate_hash_pinned_and_field_independent():
    # Pinned value: generate_hash hashes an explicit field list, so adding new
    # fields to Transaction must never change existing filenames. This guards the
    # regression the mocked fixture above cannot catch.
    transactions = [
        Transaction(transaction_date="2023-01-01", description="foo", amount="10.00", direction="CR"),
        Transaction(transaction_date="2023-01-02", description="bar", amount="5.00"),
    ]
    statement = SimpleNamespace(transactions=transactions)
    assert generate_hash(statement) == "374c20"


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
