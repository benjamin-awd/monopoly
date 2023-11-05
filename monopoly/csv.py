import logging
import os
from datetime import datetime
from typing import Optional
from uuid import uuid4

from pandas import DataFrame

from monopoly.config import StatementConfig
from monopoly.constants import ROOT_DIR
from monopoly.statement import Statement


def generate_name(
    format_type: str, config: StatementConfig, statement_date: datetime
) -> str:
    bank_name = config.bank_name
    account_type = config.account_type
    year = statement_date.year
    month = statement_date.month

    filename = f"{bank_name}-{account_type}-{year}-{month:02d}"

    if format_type == "blob":
        return (
            f"bank_name={bank_name}/"
            f"account_type={account_type}/"
            f"year={year}/"
            f"month={month}/"
            f"{filename}-{uuid4().hex[0:8]}.csv"
        )

    if format_type == "file":
        return f"{filename}.csv"

    raise ValueError("Invalid format_type")


def write_to_csv(df: DataFrame, csv_file_path: Optional[str], statement: Statement):
    logger = logging.getLogger(__name__)

    if not csv_file_path:
        filename = generate_name("file", statement.config, statement.statement_date)
        csv_file_path = os.path.join(ROOT_DIR, "output", filename)
        logger.info("Writing CSV to file path: %s", csv_file_path)

    df.to_csv(csv_file_path, index=False)

    return csv_file_path
