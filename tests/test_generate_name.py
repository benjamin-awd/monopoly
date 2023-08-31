from monopoly.banks.dataclasses import Bank
from monopoly.helpers import generate_name


def test_generate_blob_name(bank: Bank):
    expected_blob_name = (
        "bank=Example Bank/"
        "account_name=Savings/"
        "year=2023/"
        "month=8/"
        "statement.csv"
    )

    actual_blob_name = generate_name("blob", bank)
    assert expected_blob_name == actual_blob_name


def test_generate_file_name(bank: Bank):
    expected_file_name = "Example Bank-Savings-2023-08.csv"

    actual_file_name = generate_name("file", bank)

    assert expected_file_name == actual_file_name
