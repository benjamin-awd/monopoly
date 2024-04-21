from datetime import datetime
from hashlib import sha256

from fitz import Document

from monopoly.config import StatementConfig


def generate_hash(document: Document) -> str:
    """
    Generates a hash based on PDF metadata
    """
    hash_object = sha256()
    hash_object.update(str(document.metadata).encode("utf-8"))
    file_hash = hash_object.hexdigest()[0:6]
    return file_hash


def generate_name(
    document: Document,
    format_type: str,
    statement_config: StatementConfig,
    statement_type: str,
    statement_date: datetime,
) -> str:
    """
    Generates a new file name, depending on: bank, account type, statement date,
    and old file name.

    e.g. 20230720.pdf -> hsbc-credit-2023-06-b960bf1e.csv

    The appended UUID ensures that two statements from the same bank in a
    month will not overwrite each other.
    """
    bank_name = statement_config.bank_name
    year = statement_date.year
    month = statement_date.month
    file_uuid = generate_hash(document)

    file_suffix = "csv"

    filename = (
        f"{bank_name}-{statement_type}-{year}-{month:02d}-{file_uuid}.{file_suffix}"
    )

    if format_type == "blob":
        return (
            f"bank_name={bank_name}/"
            f"account_type={statement_type}/"
            f"year={year}/"
            f"month={month}/"
            f"{filename}"
        )

    if format_type == "file":
        return filename

    raise ValueError("Invalid format_type")
