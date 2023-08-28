from monopoly.banks.statement import BankStatement
from monopoly.helpers import generate_name


def test_generate_blob_name(bank_statement: BankStatement):
    expected_blob_name = (
        "bank=Example Bank/"
        "account_name=Savings/"
        "year=2023/"
        "month=8/"
        "statement.csv"
    )

    actual_blob_name = generate_name("blob", bank_statement)
    assert expected_blob_name == actual_blob_name


def test_generate_file_name(bank_statement: BankStatement):
    expected_file_name = "Example Bank-Savings-2023-08.csv"

    actual_file_name = generate_name("file", bank_statement)

    assert expected_file_name == actual_file_name
