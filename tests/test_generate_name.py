from datetime import datetime

from monopoly.helpers import generate_blob_name, generate_file_name


def test_generate_blob_name():
    bank = "Example Bank"
    account_name = "Savings"
    statement_date = datetime(2023, 8, 1)
    filename = "statement.csv"

    expected_blob_name = (
        "bank=Example Bank/"
        "account_name=Savings/"
        "year=2023/"
        "month=8/"
        "statement.csv"
    )

    actual_blob_name = generate_blob_name(bank, account_name, statement_date, filename)
    assert expected_blob_name == actual_blob_name


def test_generate_file_name():
    bank = "Example Bank"
    account_name = "Savings"
    statement_date = datetime(2023, 8, 1)

    expected_file_name = "Example Bank-Savings-2023-08.csv"

    actual_file_name = generate_file_name(bank, account_name, statement_date)

    assert expected_file_name == actual_file_name
