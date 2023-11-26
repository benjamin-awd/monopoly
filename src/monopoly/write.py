from datetime import datetime
from hashlib import md5
from pathlib import Path

from monopoly.config import StatementConfig


def generate_name(
    file_path: Path, format_type: str, config: StatementConfig, statement_date: datetime
) -> str:
    """
    Generates a new file name, depending on: bank, account type, statement date,
    and old file name.

    e.g. 20230720.pdf -> hsbc-credit-2023-06-b960bf1e.csv

    The appeneded UUID ensures that two statements from the same bank in a
    month will not overwrite each other.
    """
    bank_name = config.bank_name
    account_type = config.account_type
    year = statement_date.year
    month = statement_date.month
    file_uuid = md5(file_path.name.encode("utf-8")).hexdigest()[:6]

    file_suffix = "csv"

    filename = (
        f"{bank_name}-{account_type}-{year}-{month:02d}-{file_uuid}.{file_suffix}"
    )

    if format_type == "blob":
        return (
            f"bank_name={bank_name}/"
            f"account_type={account_type}/"
            f"year={year}/"
            f"month={month}/"
            f"filename"
        )

    if format_type == "file":
        return filename

    raise ValueError("Invalid format_type")
