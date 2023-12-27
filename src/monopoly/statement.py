import logging
import re
from datetime import datetime
from functools import cached_property
from typing import Any, Optional

import fitz
from pandas import DataFrame
from pydantic import field_validator, model_validator
from pydantic.dataclasses import dataclass
from pydantic_core import ArgsKwargs

from monopoly.config import StatementConfig
from monopoly.constants import AccountType, StatementFields
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
        Converts transactions with a suffix of "CR" to positive
        """
        if self.suffix == "CR":
            self.amount = abs(self.amount)

        else:
            self.amount = -abs(self.amount)
        return self


class Statement:
    """
    A dataclass representation of a bank statement, containing
    the PDF pages (their raw text representation in a `list`),
    and specific config per processor.
    """

    warning_message = "Safety check failed - transactions may be missing or inaccurate"

    def __init__(
        self,
        document: fitz.Document,
        pages: list[PdfPage],
        credit_config: StatementConfig,
        debit_config: Optional[StatementConfig],
    ):
        self.columns: list[str] = [enum.value for enum in StatementFields]
        self.pages = pages
        self.document = document
        self.credit_config = credit_config
        self.debit_config = debit_config

    @cached_property
    def statement_config(self) -> StatementConfig:
        if self.account_type == AccountType.DEBIT:
            if self.debit_config:
                return self.debit_config
            raise RuntimeError("Statement config not defined")
        return self.credit_config

    @cached_property
    def transactions(self) -> list[Transaction]:
        pattern = re.compile(self.statement_config.transaction_pattern)
        transactions: list[Transaction] = []

        for page in self.pages:
            for i, line in enumerate(page.lines):
                transaction = self._process_line(
                    line, page.lines, idx=i, pattern=pattern
                )
                if transaction:
                    transactions.append(transaction)

        return transactions

    def _process_line(
        self,
        line: str,
        lines: list[str],
        idx: int,
        pattern: re.Pattern,
    ) -> Transaction | None:
        if match := pattern.search(line):
            groupdict = match.groupdict()

            if self.statement_config.multiline_transactions and idx < len(lines) - 1:
                description = self.get_multiline_description(line, lines, idx, pattern)
                groupdict[StatementFields.DESCRIPTION] = description

            transaction = Transaction(**groupdict)  # type: ignore
            return transaction
        return None

    def get_multiline_description(
        self, current_line: str, lines: list[str], idx: int, pattern: re.Pattern
    ) -> str:
        if match := pattern.search(current_line):
            groupdict = match.groupdict()

        description_pos = current_line.find(groupdict[StatementFields.DESCRIPTION])

        for next_line in lines[idx + 1 :]:  # noqa: E203
            # if transaction found on next line or if next
            # line is blank, don't add the description
            if re.search(pattern, next_line) or next_line == "":
                break

            # don't process line if the description across both lines
            # doesn't align with a margin of three spaces
            next_line_text = next_line.strip()
            next_line_start_pos = next_line.find(next_line_text.split(" ")[0])

            if abs(description_pos - next_line_start_pos) > 3:
                break

            # if the next line contains "total" or "balance carried forward"
            # assume it's the end of the bank statement and exclude it
            # from the description
            if match := re.search(r"^[a-zA-Z0-9_ ][^\d]*", next_line):
                description = match.group(0).lower().strip()
                if description in ("total", "balance carried forward"):
                    break

            groupdict[StatementFields.DESCRIPTION] += " " + next_line

        return groupdict[StatementFields.DESCRIPTION]

    @cached_property
    def statement_date(self) -> datetime:
        config = self.statement_config
        first_page = self.pages[0].raw_text
        if match := re.findall(config.statement_date_pattern, first_page):
            return datetime.strptime(match[0], config.statement_date_format)
        raise ValueError("Statement date not found")

    @cached_property
    def account_type(self) -> str:
        config = self.debit_config
        if config and config.debit_account_identifier:
            for line in self.pages[0].lines:
                if re.search(config.debit_account_identifier, line):
                    return AccountType.DEBIT
        return AccountType.CREDIT

    @staticmethod
    def get_decimal_numbers(lines: list[str]) -> set[float]:
        """Returns all decimal numbers in a statement. This is used
        to perform a safety check, to make sure no transactions have been missed"""

        number_pattern = re.compile(r"[\d.,]+")
        decimal_pattern = re.compile(r"\d+\.\d+$")
        numbers: set[str] = set()
        for line in lines:
            numbers.update(number_pattern.findall(line))
            numbers = {number.replace(",", "") for number in numbers}
            decimal_numbers = {
                float(number) for number in numbers if decimal_pattern.match(number)
            }
        return decimal_numbers

    @cached_property
    def df(self) -> DataFrame:
        return DataFrame(self.transactions, columns=self.columns)

    def perform_safety_check(self) -> bool:
        """Placeholder for perform_safety_check method, which should
        exist in any child class of Statement"""
        raise NotImplementedError(
            "Subclasses must implement perform_safety_check method"
        )

    def get_all_numbers_from_document(self) -> set:
        """
        Iterates over each page in a statement, and retrieves
        all decimal numbers in each page. This is used by child classes with
        implementations of perform_safety_check()
        """
        numbers = set()

        for page in self.document:
            lines = page.get_textpage().extractText().split("\n")
            numbers.update(self.get_decimal_numbers(lines))
        return numbers
