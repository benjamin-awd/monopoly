from datetime import datetime
from hashlib import sha256

from monopoly.config import StatementConfig
from monopoly.statements import CreditStatement, DebitStatement


def generate_hash(statement: CreditStatement | DebitStatement) -> str:
    """
    Generates a hash based on PDF metadata
    """
    hash_object = sha256()
    hash_object.update(str(statement.transactions).encode("utf-8"))
    file_hash = hash_object.hexdigest()[0:6]
    return file_hash


def generate_name(
    statement: CreditStatement | DebitStatement,
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
    file_uuid = generate_hash(statement)

    filename = f"{bank_name}-{statement_type}-{year}-{month:02d}-{file_uuid}.csv"

    formats = {
        "blob": (
            f"bank_name={bank_name}/"
            f"account_type={statement_type}/"
            f"statement_date={statement_date.isoformat()[:10]}/"
            f"{filename}"
        ),
        "file": filename,
    }

    if format_type in formats:
        return formats[format_type]

    raise ValueError("Invalid format_type")
