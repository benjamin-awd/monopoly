from monopoly.helpers import generate_name
from monopoly.pdf import PDF


def test_generate_blob_name(pdf: PDF):
    expected_blob_name = (
        "bank=Example Bank/"
        "account_name=Savings/"
        "year=2023/"
        "month=8/"
        "statement.csv"
    )

    actual_blob_name = generate_name("blob", pdf.statement)
    assert expected_blob_name == actual_blob_name


def test_generate_file_name(pdf: PDF):
    expected_file_name = "Example Bank-Savings-2023-08.csv"

    actual_file_name = generate_name("file", pdf.statement)

    assert expected_file_name == actual_file_name
