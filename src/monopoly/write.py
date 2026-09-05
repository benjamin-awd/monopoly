from datetime import datetime
from hashlib import sha256

from monopoly.statements import BaseStatement


def generate_hash(statement: BaseStatement) -> str:
    """
    Generate a short filename UUID from the statement's transactions.

    Hashes an explicit list of the core transaction fields rather than the
    dataclass repr, so adding new fields to Transaction never churns filenames.

    `direction` is coerced to a plain string: it is a `Direction` enum member,
    whose repr is `<Direction.CREDIT: 'credit'>` rather than `'credit'`, and
    letting that reach `repr()` would rewrite every generated filename.
    """
    hash_object = sha256()
    identities = [
        (tx.date, tx.description, tx.amount, str(tx.direction) if tx.direction else None, tx.balance)
        for tx in statement.transactions
    ]
    hash_object.update(repr(identities).encode("utf-8"))
    return hash_object.hexdigest()[0:6]


def generate_name(
    statement: BaseStatement,
    format_type: str,
    bank_name: str,
    statement_type: str,
    statement_date: datetime,
) -> str:
    """
    Generate a new file name, depending on: bank, account type, statement date, and old file name.

    e.g. 20230720.pdf -> hsbc-credit-2023-06-b960bf1e.csv

    The appended UUID ensures that two statements from the same bank in a
    month will not overwrite each other.
    """
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

    msg = "Invalid format_type"
    raise ValueError(msg)
