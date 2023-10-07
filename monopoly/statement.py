import logging
import re
from datetime import datetime
from functools import cached_property
from typing import Annotated

from pandas import DataFrame
from pydantic import StringConstraints
from pydantic.dataclasses import dataclass

from monopoly.config import arbitrary_config
from monopoly.helpers.constants import AccountType, BankNames, BankStatement
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)


@dataclass
class StatementConfig:
    bank_name: BankNames
    account_type: AccountType
    statement_date_format: Annotated[str, StringConstraints(pattern="%.+%.+%")]
    transaction_pattern: str
    transaction_date_format: Annotated[str, StringConstraints(pattern="%")]
    date_pattern: str
    multiline_transactions: bool = False

    # Convert enums to strings
    def __post_init__(self):
        self.bank_name = self.bank_name.value
        self.account_type = self.account_type.value


@dataclass
class Transaction:
    date: str
    description: str
    amount: float


@dataclass(config=arbitrary_config)
class Statement:
    pages: list[PdfPage]
    columns = [enum.value for enum in BankStatement]
    config: StatementConfig

    @cached_property
    def transactions(self) -> list[dict]:
        transactions = []
        for page in self.pages:
            for i, line in enumerate(page.lines):
                transaction = self._process_line(line, page.lines, idx=i)
                if transaction:
                    transactions.append(transaction)

        return transactions

    def _process_line(self, line: str, lines: list[str], idx: int) -> dict:
        if match := re.search(self.config.transaction_pattern, line):
            transaction = Transaction(**match.groupdict())

            if self.config.multiline_transactions and idx < len(lines) - 1:
                next_line = lines[idx + 1]
                if not re.search(self.config.transaction_pattern, next_line):
                    transaction.description += " " + next_line

            return transaction
        return None

    @cached_property
    def statement_date(self):
        logger.info("Extracting statement date")
        first_page = self.pages[0]
        for line in first_page.lines:
            if match := re.findall(self.config.date_pattern, line):
                statement_date = match[0]
                logger.debug("Statement date found")
                return datetime.strptime(
                    statement_date, self.config.statement_date_format
                )
        return None

    @cached_property
    def df(self) -> DataFrame:
        return DataFrame(self.transactions, columns=self.columns)
