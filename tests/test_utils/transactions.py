import csv
from pathlib import Path

from monopoly.statements import Transaction


def read_pages(directory: Path) -> list[str]:
    """Read redacted/synthetic page_*.txt files from a fixture directory, in page order."""
    return [path.read_text(encoding="utf8") for path in sorted(directory.glob("page_*.txt"))]


def read_transactions_from_csv(directory: Path, file_name: str) -> list[dict[str, str]]:
    with open(directory / file_name) as file:
        return list(csv.DictReader(file))


def get_transactions_as_dict(transactions: list[Transaction]) -> list[dict[str, str]]:
    return [transaction.as_raw_dict() for transaction in transactions]
