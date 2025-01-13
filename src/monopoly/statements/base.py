import logging
import re
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property, lru_cache
from typing import Optional

from dateparser import parse

from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import Columns, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.pdf import PdfPage
from monopoly.statements.transaction import (
    Transaction,
    TransactionGroupDict,
    TransactionMatch,
)

# pylint: disable=bad-classmethod-argument
logger = logging.getLogger(__name__)


@dataclass
class MatchContext:
    line: str
    lines: list[str]
    idx: int
    description: str
    multiline_config: Optional[MultilineConfig] = None


class BaseStatement(ABC):
    """
    A dataclass representation of a bank statement, containing
    the PDF pages (their raw text representation in a `list`),
    and specific bank config.
    """

    statement_type = "base"
    columns: list[str] = [
        Columns.DATE,
        Columns.DESCRIPTION,
        Columns.AMOUNT,
    ]

    def __init__(
        self,
        pages: list[PdfPage],
        bank_name: str,
        config: StatementConfig,
        header: str,
    ):
        self.config = config
        self.bank_name = bank_name
        self.pages = pages
        self.header = header

    @cached_property
    def number_pattern(self) -> re.Pattern:
        return re.compile(r"[\d.,]+")

    @cached_property
    def decimal_pattern(self) -> re.Pattern:
        return re.compile(r"\d+\.\d+$")

    @cached_property
    def subtotal_pattern(self) -> re.Pattern:
        return re.compile(
            rf"(?:sub\stotal.*?)\s+{SharedPatterns.AMOUNT}", re.IGNORECASE
        )

    @property
    def pattern(self):
        pattern = self.config.transaction_pattern
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return pattern

    @lru_cache
    def get_transactions(self) -> list[Transaction] | None:
        transactions: list[Transaction] = []

        for page_num, page in enumerate(self.pages):
            for line_num, line in enumerate(page.lines):
                if match := self.pattern.search(line):
                    if self._check_bound(match):
                        continue

                    groupdict = TransactionGroupDict(**match.groupdict())
                    transaction_match = TransactionMatch(
                        groupdict, match, page_number=page_num
                    )
                    match = self.pre_process_match(transaction_match)
                    context = MatchContext(
                        line=line,
                        lines=page.lines,
                        idx=line_num,
                        description=match.groupdict.description,
                        multiline_config=self.config.multiline_config,
                    )
                    processed_match = self.process_match(match, context)
                    transaction = Transaction(
                        **processed_match.groupdict,
                        auto_polarity=self.config.transaction_auto_polarity,
                    )
                    transactions.append(transaction)

        if not transactions:
            return None

        post_processed_transactions = self.post_process_transactions(transactions)
        return post_processed_transactions

    def _check_bound(self, match: re.Match):
        if bound := self.config.transaction_bound:
            if match.span(Columns.AMOUNT)[0] >= bound:
                logger.debug("Transaction exists beyond boundary, ignoring")
                return True
        return False

    def pre_process_match(
        self, transaction_match: TransactionMatch
    ) -> TransactionMatch:
        return transaction_match

    def post_process_transactions(
        self, transactions: list[Transaction]
    ) -> list[Transaction]:
        return transactions

    def process_match(
        self, match: TransactionMatch, context: MatchContext
    ) -> TransactionMatch:
        # early exit if no multiline config
        if not context.multiline_config:
            return match

        if context.idx < len(context.lines) - 1:
            multiline_description = self.get_multiline_description(context)
            match.groupdict.description = multiline_description
        return match

    def get_multiline_description(
        self,
        context: MatchContext,
    ) -> str:
        """
        Combines a transaction description spanning multiple lines into a single string.
        """

        def get_start_pos(line: str) -> int:
            """Returns the starting position of the first word in a line."""
            stripped_line = line.strip()
            return line.find(stripped_line.split(" ")[0]) if stripped_line else -1

        def is_within_margin(pos1: int, pos2: int, margin: int) -> bool:
            """Checks if two positions are within a specified margin."""
            return abs(pos1 - pos2) <= margin

        def should_skip_line(next_line: str, description_pos: int) -> bool:
            """Determines if the next line should be added to the description."""
            if not next_line.strip():
                return True  # Blank line
            if self.pattern.search(next_line):
                return True  # Transaction line
            next_line_start_pos = get_start_pos(next_line)
            if not is_within_margin(description_pos, next_line_start_pos, 3):
                return True
            next_line_words = next_line_words_pattern.search(next_line)
            next_line_numbers = next_line_numbers_pattern.search(next_line)
            if next_line_words and next_line_numbers:
                _, words_end_pos = next_line_words.span()
                numbers_start_pos, _ = next_line_numbers.span()
                if (
                    numbers_start_pos > words_end_pos
                    and numbers_start_pos - words_end_pos > 20
                ):
                    return True  # Likely a footer line
            return False

        description = context.description
        description_pos = context.line.find(description)
        next_line_words_pattern = re.compile(r"\s[A-Za-z]+")
        next_line_numbers_pattern = re.compile(SharedPatterns.AMOUNT)

        if config := context.multiline_config:
            margin = config.include_prev_margin

        # Include previous line if within margin
        if margin and context.idx > 0:
            prev_line = context.lines[context.idx - 1].strip()
            if prev_line and not self.pattern.search(prev_line):
                prev_line_start_pos = get_start_pos(prev_line)
                if is_within_margin(description_pos, prev_line_start_pos, margin):
                    description = f"{prev_line} {description}"

        # Include subsequent lines
        for next_line in context.lines[context.idx + 1 :]:  # noqa: E203
            if should_skip_line(next_line, description_pos):
                break
            description += f" {next_line.strip()}"

        return description

    @property
    def failed_safety_message(self) -> str:
        return "Safety check failed - transactions may be inaccurate"

    @cached_property
    def transactions(self):
        return self.get_transactions()

    @cached_property
    def statement_date(self) -> datetime:
        pattern = self.config.statement_date_pattern
        allowed_patterns = (re.Pattern, ISO8601)
        if not isinstance(pattern, allowed_patterns):
            raise TypeError(
                f"Pattern must be one of {allowed_patterns}, not {type(pattern)}"
            )

        for page in self.pages:
            for line in page.lines:
                if match := pattern.search(line):
                    statement_date = parse(
                        date_string=match.group(1),
                        settings=self.config.statement_date_order.settings,
                    )
                    if statement_date:
                        return statement_date
                    logger.info("Unable to parse statement date %s", match.group(1))
        raise ValueError("Statement date not found")

    def get_decimal_numbers(self, lines: list[str]) -> set[float]:
        """Returns all decimal numbers in a statement. This is used
        to perform a safety check, to make sure no transactions have been missed"""

        numbers: set[str] = set()
        for line in lines:
            numbers.update(self.number_pattern.findall(line))
            numbers = {number.replace(",", "") for number in numbers}
            decimal_numbers = {
                float(number)
                for number in numbers
                if self.decimal_pattern.match(number)
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
        subtotals: list[str] = []
        for page in self.pages:
            for line in page.lines:
                if match := self.subtotal_pattern.search(line):
                    subtotals.append(match.groupdict()[Columns.AMOUNT])
        cleaned_subtotals = [float(amount.replace(",", "")) for amount in subtotals]
        return sum(cleaned_subtotals)


class SafetyCheckError(Exception):
    """Raised during the safety check if a number representing
    the total sum of transactions cannot be found in the document"""
