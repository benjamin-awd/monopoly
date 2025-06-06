import logging
import re
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import ClassVar

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

DESCRIPTION_MARGIN = 3  # Allowed margin for description position difference
MIN_BREAK_GAP = 20  # Minimum gap between words and numbers to trigger break


@dataclass
class MatchContext:
    line: str
    lines: list[str]
    idx: int
    description: str
    multiline_config: MultilineConfig | None = None


class DescriptionExtractor:
    """Handles extraction and combination of multiline descriptions."""

    def __init__(self, pattern: re.Pattern):
        self.pattern = pattern

    def get_multiline_description(self, context: MatchContext) -> str | None:
        """Combine a transaction description spanning multiple lines into a single string."""
        if not context.multiline_config:
            return None

        builder = DescriptionBuilder(
            initial_description=context.description,
            description_pos=context.line.find(context.description),
            pattern=self.pattern,
        )

        # Handle previous line if within margin
        margin = context.multiline_config.include_prev_margin
        if margin and context.idx > 0:
            builder.include_previous_line(context.lines[context.idx - 1], margin)

        # Include subsequent lines until a break condition is met
        for next_line in context.lines[context.idx + 1 :]:
            if builder.should_break_at_line(next_line):
                break
            builder.append_line(next_line)

        return builder.get_result()


class DescriptionBuilder:
    """Handles the building and validation of multiline descriptions."""

    def __init__(
        self,
        initial_description: str,
        description_pos: int,
        pattern: re.Pattern,
    ):
        self.description = initial_description
        self.description_pos = description_pos
        self.pattern = pattern
        self.words_pattern = re.compile(r"\s[A-Za-z]+")
        self.numbers_pattern = re.compile(SharedPatterns.AMOUNT)

    @staticmethod
    def get_start_pos(line: str) -> int:
        """Return the starting position of the first word in a line."""
        stripped = line.strip()
        return line.find(stripped.split(" ")[0]) if stripped else -1

    @staticmethod
    def is_within_margin(pos1: int, pos2: int, margin: int) -> bool:
        """Check if two positions are within a specified margin."""
        return abs(pos1 - pos2) <= margin

    def should_break_at_line(self, line: str) -> bool:
        """Determine if processing should stop at the current line."""
        # Blank line
        if not line.strip():
            return True

        # Transaction line
        if self.pattern.search(line):
            return True

        next_pos = self.get_start_pos(line)
        if not self.is_within_margin(self.description_pos, next_pos, DESCRIPTION_MARGIN):
            return True

        words_match = self.words_pattern.search(line)
        numbers_match = self.numbers_pattern.search(line)

        # Exclude footer lines
        if words_match and numbers_match:
            words_end = words_match.span()[1]
            numbers_start = numbers_match.span()[0]
            return numbers_start > words_end and numbers_start - words_end > MIN_BREAK_GAP

        return False

    def include_previous_line(self, prev_line: str, margin: int) -> None:
        """Attempt to include the previous line in the description."""
        prev_line = prev_line.strip()
        if not prev_line or self.pattern.search(prev_line):
            return

        prev_pos = self.get_start_pos(prev_line)
        if self.is_within_margin(self.description_pos, prev_pos, margin):
            self.description = f"{prev_line} {self.description}"

    def append_line(self, line: str) -> None:
        """Append a new line to the current description."""
        self.description += f" {line.strip()}"

    def get_result(self) -> str:
        """Return the final combined description."""
        return self.description


class BaseStatement:
    """
    A dataclass representation of a bank statement.

    Contains PDF pages (their raw text representation in a `list`), and specific bank config.
    """

    statement_type = "base"
    columns: ClassVar[list[str]] = [
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
        return re.compile(rf"(?:sub\stotal.*?)\s+{SharedPatterns.AMOUNT}", re.IGNORECASE)

    @property
    def pattern(self):
        pattern = self.config.transaction_pattern
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return pattern

    def get_transactions(self) -> list[Transaction] | None:
        transactions: list[Transaction] = []

        for page_num, page in enumerate(self.pages):
            for line_num, line in enumerate(page.lines):
                if match := self.pattern.search(line):
                    if self._check_bound(match):
                        continue

                    groupdict = TransactionGroupDict(**match.groupdict())
                    transaction_match = TransactionMatch(groupdict, match, page_number=page_num)
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

        return self.post_process_transactions(transactions)

    def _check_bound(self, match: re.Match):
        if (bound := self.config.transaction_bound) and match.span(Columns.AMOUNT)[0] >= bound:
            logger.debug("Transaction exists beyond boundary, ignoring")
            return True
        return False

    def pre_process_match(self, transaction_match: TransactionMatch) -> TransactionMatch:
        return transaction_match

    def post_process_transactions(self, transactions: list[Transaction]) -> list[Transaction]:
        return transactions

    def process_match(self, match: TransactionMatch, context: MatchContext) -> TransactionMatch:
        # early exit if no multiline config
        if not context.multiline_config:
            return match

        # early exit if end of page
        if context.idx > len(context.lines) - 1:
            return match

        if context.multiline_config.multiline_polarity:
            match.groupdict.polarity = self.get_multiline_polarity(context)

        if context.multiline_config.multiline_descriptions:
            multiline_description = self.get_multiline_description(context)
            match.groupdict.description = multiline_description
        return match

    def get_multiline_polarity(self, context: MatchContext):
        """
        Pull polarity from the next line, if it can be found on the next line.

        e.g.
        Date                           Description                            Amount
        ----------------------------------------------------------------------------
        24.02.25                       PAYMENT RECEIVED - THANK YOU            79.99
                                                                                  CR

        In this case, the polarity will resolve to CR.
        """
        if re.match(SharedPatterns.POLARITY, context.lines[context.idx + 1]):
            return context.lines[context.idx + 1].strip()
        return None

    def get_multiline_description(
        self,
        context: MatchContext,
    ) -> str:
        """Combine a transaction description spanning multiple lines into a single string."""
        extractor = DescriptionExtractor(self.pattern)
        return extractor.get_multiline_description(context) or ""

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
            msg = f"Pattern must be one of {allowed_patterns}, not {type(pattern)}"
            raise TypeError(msg)

        for page in self.pages:
            lines = page.lines

            for i, line in enumerate(lines):
                text = self._get_search_text(lines, i, line)

                if match := pattern.search(text):
                    date_string = self._construct_date_string(match)
                    statement_date = parse(
                        date_string=date_string,
                        settings=self.config.statement_date_order.settings,
                    )
                    if statement_date:
                        return statement_date
                    logger.info("Unable to parse statement date %s", date_string)
        msg = "Statement date not found"
        raise ValueError(msg)

    @staticmethod
    def _construct_date_string(match: re.Match):
        """Construct date with named groups 'day', 'month', and 'year' if they exist, otherwise use group 1."""
        if {"day", "month", "year"}.issubset(match.groupdict()):
            day = match.group("day")
            month = match.group("month")
            year = match.group("year")

            return f"{day}-{month}-{year}"
        return match.group(1)

    def _get_search_text(self, lines, i, line):
        """Get text to search, optionally combining multiple lines and removing whitespace."""
        if not self.config.multiline_config:
            return line

        if self.config.multiline_config.multiline_statement_date:
            return " ".join(" ".join(lines[i : i + 3]).split())

        return line

    def get_decimal_numbers(self, lines: list[str]) -> set[float]:
        """
        Return all decimal numbers in a statement.

        This is used to perform a safety check, to make sure no transactions have been missed.
        """
        numbers: set[str] = set()
        for line in lines:
            numbers.update(self.number_pattern.findall(line))
            numbers = {number.replace(",", "") for number in numbers}
            decimal_numbers = {float(number) for number in numbers if self.decimal_pattern.match(number)}
        return decimal_numbers

    def perform_safety_check(self) -> bool:
        """Mandate the perform_safety_check method, which should exist in any child class of Statement."""
        msg = "Subclasses must implement perform_safety_check method"
        raise NotImplementedError(msg)

    def get_all_numbers_from_document(self) -> set:
        """
        Iterate over each page in a statement, and retrieves all decimal numbers in each page.

        This is used by child classes with implementations of perform_safety_check().
        """
        numbers = set()

        for page in self.pages:
            lines = page.lines
            numbers.update(self.get_decimal_numbers(lines))
        numbers.add(self.get_subtotal_sum())
        return numbers

    def get_subtotal_sum(self):
        """
        Retrieve the subtotals from a document, and calculates the total.

        Useful for statements that don't give a total figure over
        several cards/months in a single statement.
        """
        subtotals: list[str] = []
        for page in self.pages:
            subtotals.extend(
                match.groupdict()[Columns.AMOUNT]
                for line in page.lines
                if (match := self.subtotal_pattern.search(line))
            )
        cleaned_subtotals = [float(amount.replace(",", "")) for amount in subtotals]
        return sum(cleaned_subtotals)


class SafetyCheckError(Exception):
    """Raised if safety check fails."""
