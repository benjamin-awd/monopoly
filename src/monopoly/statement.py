import logging
import re
from datetime import datetime
from functools import cached_property

from pandas import DataFrame
from pydantic import field_validator
from pydantic.dataclasses import dataclass

from monopoly.config import StatementConfig, TransactionConfig
from monopoly.constants import StatementFields
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """
    Holds transaction data, validates the data, and
    performs various coercions like removing whitespace

    The class attributes are consistent with the enum
    values from StatementFields
    """

    transaction_date: str
    description: str
    amount: float

    @field_validator("description", mode="after")
    def remove_extra_whitespace(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("amount", mode="before")
    def adjust_amount(cls, value: str) -> str:
        """
        Replaces commas, whitespaces and parentheses in string representation of floats
        e.g.
            1,234.00 -> 1234.00
            (-10.00) -> -10.00
            (-1.56 ) -> -1.56
        """
        if isinstance(value, str):
            # change cashback to negative transaction
            if value.startswith("(") and value.endswith(")"):
                value = "-" + value
            return re.sub(r"[,)(\s]", "", value)
        return value


@dataclass
class Statement:
    """
    A dataclass representation of a bank statement, containing
    the PDF pages (their raw text representation in a `list`),
    and specific config per bank.
    """

    pages: list[PdfPage]
    columns = [enum.value for enum in StatementFields]
    statement_config: StatementConfig
    transaction_config: TransactionConfig
    prev_month_balance = None

    @cached_property
    def transactions(self) -> list[Transaction]:
        transactions = []
        for page in self.pages:
            lines = self.process_lines(page)
            for i, line in enumerate(lines):
                transaction = self._process_line(line, lines, idx=i)
                if transaction:
                    transactions.append(transaction)

        # TODO: this breaks for statements that do not actually have a prev month balance
        # e.g. the first statement for a new credit card.
        # in such cases, no error should be raised
        if not self.prev_month_balance:
            raise ValueError("Unable to find previous month's balance")

        first_transaction_date = transactions[0].transaction_date
        prev_month_balance_transaction = Transaction(
            **self.prev_month_balance, transaction_date=first_transaction_date
        )
        prev_month_balance_transaction.amount = -abs(
            prev_month_balance_transaction.amount
        )
        transactions.insert(0, prev_month_balance_transaction)
        return transactions

    @staticmethod
    def process_lines(page: PdfPage) -> list:
        return [line.lstrip() for line in page.lines]

    def _process_line(
        self, line: str, lines: list[str], idx: int
    ) -> Transaction | None:
        if not self.prev_month_balance:
            if match := re.search(self.statement_config.prev_balance_pattern, line):
                self.prev_month_balance = match.groupdict()

        if match := re.search(self.transaction_config.pattern, line):
            # if the cashback key isn't in the description, it's not
            # a cashback transaction, and is of no interest to us
            if Statement.is_enclosed_in_parentheses(match["amount"]):
                if self.transaction_config.cashback_key not in match["description"]:
                    return None

            transaction = Transaction(**match.groupdict())  # type: ignore

            # handle transactions that span multiple lines
            if self.transaction_config.multiline_transactions and idx < len(lines) - 1:
                next_line = lines[idx + 1]
                if not re.search(self.transaction_config.pattern, next_line):
                    transaction.description += " " + next_line
                    transaction = Transaction(**vars(transaction))
            return transaction
        return None

    @staticmethod
    def is_enclosed_in_parentheses(amount: str) -> bool:
        return amount.startswith("(") and amount.endswith(")")

    @cached_property
    def raw_statement_date(self):
        config = self.statement_config
        logger.debug("Extracting statement date")
        first_page = self.pages[0]
        for line in first_page.lines:
            if match := re.findall(config.statement_date_pattern, line):
                logger.debug("Statement date found")
                return match[0]
        logger.debug("Statement date not found")
        return None

    @cached_property
    def statement_date(self):
        config = self.statement_config
        return datetime.strptime(self.raw_statement_date, config.statement_date_format)

    @staticmethod
    def get_decimal_numbers(lines: list[str]) -> set[float]:
        """Returns all decimal numbers in a statement. This is used
        to perform a safety check, to make sure no transactions have been missed"""

        number_pattern = re.compile(r"[\d.,]+")
        decimal_pattern = re.compile(r"\d+\.\d+$")
        numbers = set()
        for line in lines:
            numbers.update(re.findall(number_pattern, line))
            numbers = {number.replace(",", "") for number in numbers}
            decimal_numbers = {
                float(number) for number in numbers if decimal_pattern.match(number)
            }
        return decimal_numbers

    @cached_property
    def df(self) -> DataFrame:
        return DataFrame(self.transactions, columns=self.columns)
