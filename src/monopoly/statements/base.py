import logging
import re
from abc import ABC
from datetime import datetime
from functools import cached_property, lru_cache
from pathlib import Path

from dateparser import parse

from monopoly.config import CreditStatementConfig, DebitStatementConfig
from monopoly.constants import Columns, SharedPatterns
from monopoly.pdf import PdfParser
from monopoly.statements.transaction import (
    Transaction,
    TransactionGroupDict,
    TransactionMatch,
)

# pylint: disable=bad-classmethod-argument
logger = logging.getLogger(__name__)


class BaseStatement(ABC):
    """
    A dataclass representation of a bank statement, containing
    the PDF pages (their raw text representation in a `list`),
    and specific bank config.
    """

    def __init__(
        self,
        parser: PdfParser,
        config: CreditStatementConfig | DebitStatementConfig,
    ):
        self.pages = parser.get_pages()
        self.config = config
        self.columns: list[str] = [
            Columns.DATE,
            Columns.DESCRIPTION,
            Columns.AMOUNT,
        ]
        self.parser = parser
        self.document = parser.document

    @property
    def bank(self):
        return self.parser.bank

    @property
    def pattern(self):
        pattern = self.config.transaction_pattern
        if not isinstance(self.config.transaction_pattern, re.Pattern):
            pattern = re.compile(self.config.transaction_pattern, re.IGNORECASE)
        return pattern

    @lru_cache
    def get_transactions(self) -> list[Transaction] | None:
        transactions: list[Transaction] = []

        for page in self.pages:
            for idx, line in enumerate(page.lines):
                if match := self.pattern.search(line):
                    groupdict = TransactionGroupDict(**match.groupdict())
                    transaction_match = TransactionMatch(groupdict, match)
                    pre_processed_match = self.pre_process_match(transaction_match)
                    processed_match = self.process_match(
                        match=pre_processed_match,
                        line=line,
                        lines=page.lines,
                        idx=idx,
                    )
                    transaction = Transaction(**processed_match.groupdict)
                    transactions.append(transaction)

        if not transactions:
            return None

        post_processed_transactions = self.post_process_transactions(transactions)
        return post_processed_transactions

    def pre_process_match(
        self, transaction_match: TransactionMatch
    ) -> TransactionMatch:
        return transaction_match

    def post_process_transactions(
        self, transactions: list[Transaction]
    ) -> list[Transaction]:
        return transactions

    def process_match(
        self,
        match: TransactionMatch,
        line: str,
        lines: list[str],
        idx: int,
    ) -> TransactionMatch:
        if self.config.multiline_transactions and idx < len(lines) - 1:
            multiline_description = self.get_multiline_description(
                match.groupdict.description, line, lines, idx
            )
            match.groupdict.description = multiline_description
        return match

    def get_multiline_description(
        self,
        description: str,
        current_line: str,
        lines: list[str],
        idx: int,
    ) -> str:
        """Checks if a transaction description spans multiple lines, and
        tries to combine them into a single string"""
        description_pos = current_line.find(description)
        for next_line in lines[idx + 1 :]:  # noqa: E203
            # if next line is blank, don't add the description
            if not next_line:
                break

            # if transaction found on next line then break
            if self.pattern.search(next_line):
                break

            # don't process line if the description across both lines
            # doesn't align with a margin of three spaces
            next_line_text = next_line.strip()
            next_line_start_pos = next_line.find(next_line_text.split(" ")[0])

            if abs(description_pos - next_line_start_pos) > 3:
                break

            # if there's an amount in the next line, and it's further than
            # 20 spaces away, we assume that this isn't part of the description
            # and is a footer line like "Total" or "Balance Carried Forward"
            next_line_words = re.search(r"\s[A-Za-z]+", next_line)
            next_line_numbers = re.search(SharedPatterns.AMOUNT, next_line)

            if next_line_words and next_line_numbers:
                _, words_end_pos = next_line_words.span()
                numbers_start_pos, _ = next_line_numbers.span()

                if (
                    numbers_start_pos > words_end_pos
                    and numbers_start_pos - words_end_pos > 20
                ):
                    break

            description += " " + next_line

        return description

    @property
    def failed_safety_message(self) -> str:
        return (
            f"Safety check for {Path(self.document.name).stem} failed - "
            "transactions may be inaccurate"
        )

    @cached_property
    def transactions(self):
        return self.get_transactions()

    @cached_property
    def statement_date(self) -> datetime:
        for page in self.pages:
            for line in page.lines:
                if match := re.search(self.config.statement_date_pattern, line):
                    statement_date = parse(
                        date_string=match.group(1),
                        settings=self.config.statement_date_order.settings,
                    )
                    if statement_date:
                        return statement_date
        raise ValueError("Statement date not found")

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

        for page in self.pages:
            lines = page.lines
            numbers.update(self.get_decimal_numbers(lines))
        numbers.add(self.get_subtotal_sum())
        return numbers

    def get_subtotal_sum(self):
        """
        Retrieves the subtotals from a document, and calculates the total.
        Useful for statements that don't give a total figure over
        several cards/months in a single statement.
        """
        subtotal_pattern = re.compile(
            rf"(?:sub\stotal.*?)\s+{SharedPatterns.AMOUNT}", re.IGNORECASE
        )
        subtotals: list[str] = []
        for page in self.pages:
            for line in page.lines:
                if match := subtotal_pattern.search(line):
                    subtotals.append(match.groupdict()[Columns.AMOUNT])
        cleaned_subtotals = [float(amount.replace(",", "")) for amount in subtotals]
        return sum(cleaned_subtotals)


class SafetyCheckError(Exception):
    """Raise when safety check fails"""
