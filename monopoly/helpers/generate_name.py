from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

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
