import logging
import re
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import ClassVar

from dateparser import parse

from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import Columns, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.pdf import PdfPage
from monopoly.statements.transaction import (
    Transaction,
    TransactionMatch,
)

# pylint: disable=bad-classmethod-argument
logger = logging.getLogger(__name__)

MIN_BREAK_GAP = 20  # Minimum gap between words and numbers to trigger break


@dataclass
class MatchContext:
    line: str
    lines: list[str]
    idx: int
    description: str
    multiline_config: MultilineConfig | None = None


class DescriptionBuilder:
    """
    Handles extraction and building of multiline descriptions.

    Regex patterns are pre-compiled as class attributes to avoid re-compilation loop overhead.
    """

    WORDS_PATTERN: ClassVar[re.Pattern] = re.compile(r"\s[A-Za-z]+")
    NUMBERS_PATTERN: ClassVar[re.Pattern] = re.compile(SharedPatterns.AMOUNT)

    def __init__(self, ctx: MatchContext, pattern: re.Pattern):
        self.pattern = pattern
        self.ctx = ctx
        self.cfg = ctx.multiline_config
        self.description = ctx.description
        self.desc_pos = ctx.line.find(ctx.description)
        self.previous_transaction_date = None

    def build(self) -> str:
        """Build the final description string by iterating forward through lines."""
        if not self.cfg:
            return self.description

        # Handle previous line
        if self.cfg.include_prev_margin and self.ctx.idx > 0:
            self._include_previous_line()

        # Handle subsequent lines
        for next_line in self.ctx.lines[self.ctx.idx + 1 :]:
            if self._should_break(next_line):
                break
            self.description += f" {next_line.strip()}"

        return self.description

    def _should_break(self, line: str) -> bool:
        """Determine if processing should stop at the current line."""
        # cfg is guaranteed to be not None here because build() returns early if cfg is None
        if self.cfg is None:
            return True

        if not line.strip() or self.pattern.search(line):
            return True

        next_pos = self._get_start_pos(line)
        if next_pos != -1 and not self._is_within_margin(self.desc_pos, next_pos, self.cfg.description_margin):
            return True

        words_match = self.WORDS_PATTERN.search(line)
        nums_match = self.NUMBERS_PATTERN.search(line)

        # Heuristic: Exclude footer lines containing detached numbers/words
        if words_match and nums_match:
            words_end = words_match.end()
            nums_start = nums_match.start()
            if nums_start > words_end and (nums_start - words_end) > MIN_BREAK_GAP:
                return True

        return False

    def _include_previous_line(self) -> None:
        """Attempt to prepend the previous line."""
        # cfg is guaranteed to be not None here because build() returns early if cfg is None
        if self.cfg is None:
            return

        prev_line = self.ctx.lines[self.ctx.idx - 1].strip()
        if not prev_line or self.pattern.search(prev_line):
            return

        prev_pos = self._get_start_pos(prev_line)
        if self._is_within_margin(self.desc_pos, prev_pos, self.cfg.include_prev_margin):
            self.description = f"{prev_line} {self.description}"

    @staticmethod
    def _get_start_pos(line: str) -> int:
        stripped = line.strip()
        return line.find(stripped.split(" ")[0]) if stripped else -1

    @staticmethod
    def _is_within_margin(pos1: int, pos2: int, margin: int | None) -> bool:
        if not margin:
            margin = 0
        return abs(pos1 - pos2) <= margin


class BaseStatement:
    """
    A dataclass representation of a bank statement.

    Contains PDF pages (their raw text representation in a list), and specific bank config.
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
        file_path: Path | None = None,
    ):
        self.config = config
        self.bank_name = bank_name
        self.pages = pages
        self.header = header
        self.file_path = file_path

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
            lines = page.lines
            for line_num, line in enumerate(lines):
                raw_match = self.pattern.search(line)
                if not raw_match:
                    continue

                if self._check_bound(raw_match):
                    continue

                # Create TransactionMatch directly from regex groupdict
                groupdict = raw_match.groupdict()
                transaction_match = TransactionMatch(
                    transaction_date=groupdict.get("transaction_date"),
                    amount=groupdict["amount"],
                    description=groupdict["description"],
                    polarity=groupdict.get("polarity"),
                    match=raw_match,
                    page_number=page_num,
                )

                transaction_match = self.pre_process_match(transaction_match)
                processed_match = self.process_match(transaction_match, lines, line_num)
                transaction = Transaction(
                    **processed_match.groupdict(),
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
        """
        Pre-process transaction match before further processing.

        Handles multiline transaction date carry-forward logic: when enabled,
        transactions without a date will inherit the most recent date seen.
        """
        multiline_config = self.config.multiline_config
        if multiline_config.multiline_transaction_date:
            if transaction_match.transaction_date:
                self.previous_transaction_date = transaction_match.transaction_date
            else:
                transaction_match.transaction_date = self.previous_transaction_date

        return transaction_match

    def post_process_transactions(self, transactions: list[Transaction]) -> list[Transaction]:
        return transactions

    def process_match(self, match: TransactionMatch, lines: list[str], line_num: int):
        ctx = MatchContext(
            line=lines[line_num],
            lines=lines,
            idx=line_num,
            description=match.description,
            multiline_config=self.config.multiline_config,
        )

        # early exit if no multiline config
        if not (cfg := ctx.multiline_config):
            return match

        # Early exit if end of page
        if ctx.idx >= len(ctx.lines) - 1:
            return match

        if cfg.multiline_polarity:
            match.polarity = self.get_multiline_polarity(ctx)

        if cfg.multiline_descriptions:
            match.description = DescriptionBuilder(ctx, self.pattern).build()

        return match

    def get_multiline_polarity(self, ctx: MatchContext):
        """
        Pull polarity from the next line, if it can be found on the next line.

        e.g.
        Date                           Description                            Amount
        ----------------------------------------------------------------------------
        24.02.25                       PAYMENT RECEIVED - THANK YOU            79.99
                                                                                  CR

        In this case, the polarity will resolve to CR.
        """
        next_line = ctx.lines[ctx.idx + 1]
        if re.match(SharedPatterns.POLARITY, next_line):
            return next_line.strip()
        return None

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

        # Fallback: Try extracting date from filename
        if filename_date := self._extract_date_from_filename():
            logger.info("Statement date extracted from filename: %s", filename_date)
            return filename_date

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

    def _extract_date_from_filename(self) -> datetime | None:
        """
        Extract statement month and year from the filename.

        Only enabled if the bank config has a filename_fallback_pattern set.

        Supports patterns like:
        - eStatement_Nov2025_2025-11-07T14_50_26.pdf
        - CardStatement_Oct2025.pdf

        Returns datetime object with day set to 1, or None if pattern not found.
        """
        file_path = self.file_path
        fallback_pattern = self.config.filename_fallback_pattern

        if not file_path or not fallback_pattern:
            return None

        filename = file_path.name

        if match := fallback_pattern.search(filename):
            month_abbr = match.group(1)
            year = match.group(2)
            date_string = f"1 {month_abbr} {year}"

            try:
                return parse(
                    date_string=date_string,
                    settings=self.config.statement_date_order.settings,
                )
            except (ValueError, TypeError) as e:
                logger.warning("Failed to parse date from filename '%s': %s", filename, e)
                return None

        return None

    def _get_search_text(self, lines, i, line):
        """Get text to search, optionally combining multiple lines and removing whitespace."""
        multiline_config = self.config.multiline_config
        if not multiline_config:
            return line

        if multiline_config.multiline_statement_date:
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
        return {float(number) for number in numbers if self.decimal_pattern.match(number)}

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
