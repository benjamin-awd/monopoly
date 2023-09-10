from datetime import datetime

from monopoly.bank import Bank
from monopoly.helpers.generate_name import generate_name


def test_generate_blob_name(bank: Bank):
    statement_date = datetime(2023, 8, 1)
    expected_blob_name = (
        "bank_name=Example Bank/"
        "account_type=Savings/"
        "year=2023/"
        "month=8/"
        "Example Bank-Savings-2023-08.csv"
    )

    actual_blob_name = generate_name("blob", bank.statement_config, statement_date)
    assert expected_blob_name == actual_blob_name


def test_generate_file_name(bank: Bank):
    statement_date = datetime(2023, 8, 1)
    expected_file_name = "Example Bank-Savings-2023-08.csv"

    actual_file_name = generate_name("file", bank.statement_config, statement_date)

    assert expected_file_name == actual_file_name
