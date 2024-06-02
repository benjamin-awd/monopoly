import csv
from pathlib import Path

from monopoly.statements import Transaction


def read_transactions_from_csv(directory: Path, file_name: str) -> list[dict[str, str]]:
    transactions = []
    with open(directory / file_name, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            transactions.append(row)
    return transactions


def get_transactions_as_dict(transactions: list[Transaction]) -> list[dict[str, str]]:
    transactions_as_dict = []
    for transaction in transactions:
        transactions_as_dict.append(transaction.as_raw_dict())
    return transactions_as_dict
