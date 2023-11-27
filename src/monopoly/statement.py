import logging
import re
from datetime import datetime
from functools import cached_property
from typing import Any, Optional

from pandas import DataFrame
from pydantic import field_validator, model_validator
from pydantic.dataclasses import dataclass
from pydantic_core import ArgsKwargs

from monopoly.config import StatementConfig, TransactionConfig
from monopoly.constants import StatementFields
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)


# pylint: disable=bad-classmethod-argument
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
    suffix: Optional[str] = None

    @field_validator("description", mode="after")
    def remove_extra_whitespace(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("amount", mode="before")
    def prepare_amount_for_float_coercion(cls, amount: str) -> str:
        """
        Replaces commas, whitespaces and parentheses in string representation of floats
        e.g.
            1,234.00 -> 1234.00
            (-10.00) -> -10.00
            (-1.56 ) -> -1.56
        """
        if isinstance(amount, str):
            return re.sub(r"[,)(\s]", "", amount)
        return amount

    @model_validator(mode="before")  # type: ignore
    def treat_parenthesis_enclosure_as_credit(self: ArgsKwargs | Any) -> "ArgsKwargs":
        """
        Treat amounts enclosed by parentheses (e.g. cashback) as a credit entry
        """
        if self.kwargs:
            amount: str = self.kwargs["amount"]
            if isinstance(amount, str):
                if amount.startswith("(") and amount.endswith(")"):
                    self.kwargs["suffix"] = "CR"
        return self

    @model_validator(mode="after")
    def convert_credit_amount_to_negative(self: "Transaction") -> "Transaction":
        """
        Converts transactions with a suffix of "CR" to negative
        """
        if self.suffix == "CR":
            self.amount = abs(self.amount)

        else:
            self.amount = -abs(self.amount)
        return self


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
        transactions: list[Transaction] = []
        for page in self.pages:
            lines = self.process_lines(page)
            for i, line in enumerate(lines):
                transaction = self._process_line(line, lines, idx=i)
                if transaction:
                    transactions.append(transaction)
        transactions = self._add_prev_month_balance(transactions)
        return transactions

    def _process_line(
        self, line: str, lines: list[str], idx: int
    ) -> Transaction | None:
        if not self.prev_month_balance:
            if match := re.search(self.statement_config.prev_balance_pattern, line):
                self.prev_month_balance = match.groupdict()

        if match := re.search(self.transaction_config.pattern, line):
            transaction = Transaction(**match.groupdict())  # type: ignore

            # handle transactions that span multiple lines
            if self.transaction_config.multiline_transactions and idx < len(lines) - 1:
                next_line = lines[idx + 1]
                if not re.search(self.transaction_config.pattern, next_line):
                    transaction.description += " " + next_line
            return transaction
        return None

    def _add_prev_month_balance(
        self, transactions: list[Transaction]
    ) -> list[Transaction]:
        """
        Converts the previous month's statement balance into a transaction,
        if it exists in the statement.
        """
        if self.prev_month_balance:
            first_transaction_date = transactions[0].transaction_date
            prev_month_balance_transaction = Transaction(
                **self.prev_month_balance,  # type: ignore
                transaction_date=first_transaction_date,
            )
            transactions.insert(0, prev_month_balance_transaction)
        if not self.prev_month_balance:
            logger.debug("Unable to find previous month's balance")
        return transactions

    @staticmethod
    def process_lines(page: PdfPage) -> list:
        return [line.lstrip() for line in page.lines]

    @cached_property
    def source_file_name_date(self) -> str:
        config = self.statement_config
        logger.debug("Extracting statement date")
        first_page = self.pages[0]
        for line in first_page.lines:
            if match := re.findall(config.date_pattern, line):
                logger.debug("Statement date found")
                return match[0]
        raise ValueError("Statement date not found")

    @cached_property
    def statement_date(self):
        config = self.statement_config
        return datetime.strptime(self.source_file_name_date, config.date_format)

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
