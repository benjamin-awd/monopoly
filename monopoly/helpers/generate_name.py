from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from monopoly.bank import StatementConfig

logger = logging.getLogger(__name__)


def generate_name(
    format_type: str, config: StatementConfig, statement_date: datetime
) -> str:
    bank_name = config.bank_name
    account_type = config.account_type
    year = statement_date.year
    month = statement_date.month

    filename = f"{bank_name}-{account_type}-{year}-{month:02d}.csv"

    if format_type == "blob":
        return (
            f"bank_name={bank_name}/"
            f"account_type={account_type}/"
            f"year={year}/"
            f"month={month}/"
            f"{filename}"
        )

    if format_type == "file":
        return filename

    raise ValueError("Invalid format_type")
