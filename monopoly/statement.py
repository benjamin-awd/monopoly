import logging
import re
from datetime import datetime
from functools import cached_property

from pandas import DataFrame
from pydantic import field_validator
from pydantic.dataclasses import dataclass

from monopoly.config import StatementConfig, arbitrary_config
from monopoly.constants import StatementFields
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    transaction_date: str
    description: str
    amount: float

    @field_validator("description", mode="after")
    def remove_extra_whitespace(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("amount", mode="before")
    def adjust_number_format(cls, value: str) -> str:
        if isinstance(value, str):
            return value.replace(",", "")
        return value


@dataclass(config=arbitrary_config)
class Statement:
    pages: list[PdfPage]
    columns = [enum.value for enum in StatementFields]
    config: StatementConfig

    @cached_property
    def transactions(self) -> list[Transaction]:
        transactions = []
        for page in self.pages:
            lines = self.process_lines(page)
            for i, line in enumerate(lines):
                transaction = self._process_line(line, lines, idx=i)
                if transaction:
                    transactions.append(transaction)

        return transactions

    @staticmethod
    def process_lines(page: PdfPage) -> list:
        return [line.lstrip() for line in page.lines]

    def _process_line(
        self, line: str, lines: list[str], idx: int
    ) -> Transaction | None:
        if match := re.search(self.config.transaction_pattern, line):
            transaction = Transaction(**match.groupdict())  # type: ignore

            if self.config.multiline_transactions and idx < len(lines) - 1:
                next_line = lines[idx + 1]
                if not re.search(self.config.transaction_pattern, next_line):
                    transaction.description += " " + next_line
                    transaction = Transaction(**vars(transaction))

            return transaction
        return None

    @cached_property
    def statement_date(self):
        logger.info("Extracting statement date")
        first_page = self.pages[0]
        for line in first_page.lines:
            if match := re.findall(self.config.statement_date_pattern, line):
                statement_date = match[0]
                logger.debug("Statement date found")
                return datetime.strptime(
                    statement_date, self.config.statement_date_format
                )
        return None

    @cached_property
    def df(self) -> DataFrame:
        return DataFrame(self.transactions, columns=self.columns)
