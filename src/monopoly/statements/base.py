import logging
import re
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import ClassVar

from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import Columns, Direction, SharedPatterns
from monopoly.pdf import PdfPage
from monopoly.statements.account_resolver import AccountResolver
from monopoly.statements.currency_resolver import CurrencyResolver
from monopoly.statements.date_resolver import DateResolver
from monopoly.statements.number_extractor import NumberExtractor
from monopoly.statements.transaction import (
    RawTransaction,
    Transaction,
)

# pylint: disable=bad-classmethod-argument
logger = logging.getLogger(__name__)

MIN_BREAK_GAP = 20  # Minimum gap between words and numbers to trigger break


# The last figure on a line, with an optional sign and currency symbol: "- $1,234.56", "+ $0.12", "100.00".
TRAILING_AMOUNT = re.compile(r"(?:[+-]\s*)?[$€£]?\d{1,3}(?:,\d{3})*\.\d{2}\s*$")


def merge_wrapped_amounts(lines: list[str], pattern: re.Pattern[str]) -> list[str]:
    """
    Lay an amount that wrapped onto the next line back onto its row's line.

    A long description can push a row's amount down a line, while its date, category and balance stay on the first:

        Mar 20   Withdrawal from EXAMPLE TAX AUTHORITY ESTIMATED TAX   Debit               $1,008.15
                 PAYMENT                                                      - $100.00

    pdftotext's layout mode keeps the columns, so the amount sits under the amount column. Copying it into the same
    columns of the line above (where they are blank) gives a whole row. The copy is kept only when the result then
    matches `pattern`, so no other line changes. The amount is taken off the next line, leaving the description's
    wrapped words for `multiline_descriptions`.
    """
    out = list(lines)
    for i in range(len(out) - 1):
        line, below = out[i], out[i + 1]
        if pattern.search(line) or pattern.search(below):
            continue
        if not (found := TRAILING_AMOUNT.search(below)):
            continue
        start, end = found.span()
        padded = line.ljust(end)
        if padded[start:end].strip():
            continue
        merged = (padded[:start] + below[start:end] + padded[end:]).rstrip()
        if pattern.search(merged):
            out[i] = merged
            out[i + 1] = below[:start].rstrip()
    return out


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

    def __init__(self, ctx: MatchContext, pattern: re.Pattern, cfg: MultilineConfig):
        self.pattern = pattern
        self.ctx = ctx
        self.cfg = cfg
        self.description = ctx.description
        self.desc_pos = ctx.line.find(ctx.description)

    def build(self) -> str:
        """Build the final description string by iterating forward through lines."""
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


class BaseStatement(ABC):
    """
    Abstract base for a bank statement.

    Contains PDF pages (their raw text representation in a list), and specific bank config.
    """

    statement_type = "base"
    #: How a bare "-" marker reads for this statement type. Debit statements
    #: print it on withdrawals, credit statements on refunds.
    minus_direction: ClassVar[Direction] = Direction.DEBIT
    columns: ClassVar[list[str]] = [
        Columns.DATE,
        Columns.DESCRIPTION,
        Columns.AMOUNT,
        Columns.BALANCE,
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
        # carried across lines when multiline_transaction_date is enabled
        self.previous_transaction_date: str | None = None

    @property
    def pattern(self) -> re.Pattern[str]:
        return self.config.transaction_pattern

    def _iter_matches(self) -> Iterator[tuple[RawTransaction, MatchContext]]:
        """Yield one raw transaction and its line context per in-bounds match."""
        for page_num, page in enumerate(self.pages):
            lines = page.lines
            if self.config.multiline_config.multiline_amount:
                lines = merge_wrapped_amounts(lines, self.pattern)
            for line_num, line in enumerate(lines):
                raw_match = self.pattern.search(line)
                if not raw_match or self._check_bound(raw_match):
                    continue

                groupdict = raw_match.groupdict()
                raw_transaction = RawTransaction(
                    match=raw_match,
                    page_number=page_num,
                    description=groupdict[Columns.DESCRIPTION],
                    amount=groupdict[Columns.AMOUNT],
                    transaction_date=groupdict.get("transaction_date"),
                    posting_date=groupdict.get("posting_date"),
                    direction=groupdict.get(Columns.DIRECTION),
                    balance=groupdict.get(Columns.BALANCE),
                )
                context = MatchContext(
                    line=line,
                    lines=lines,
                    idx=line_num,
                    description=raw_transaction.description,
                    multiline_config=self.config.multiline_config,
                )
                yield raw_transaction, context

    def _build_transaction(self, raw_transaction: RawTransaction, context: MatchContext) -> Transaction:
        """Run the pre/post-processing hooks and construct the Transaction."""
        account = self.account_resolver.at(raw_transaction.page_number, context.idx)
        currency = self.currency_resolver.at(raw_transaction.page_number, context.idx)
        processed = self.process_match(self.pre_process_match(raw_transaction), context)
        return Transaction(
            **processed.as_dict(),
            currency=currency,
            account=account,
            auto_direction=self.config.transaction_auto_direction,
        )

    def get_transactions(self) -> list[Transaction]:
        transactions = [self._build_transaction(raw, ctx) for raw, ctx in self._iter_matches()]
        return self.post_process_transactions(transactions)

    def _check_bound(self, match: re.Match):
        if (bound := self.config.transaction_bound) and match.span(Columns.AMOUNT)[0] >= bound:
            logger.debug("Transaction exists beyond boundary, ignoring")
            return True
        return False

    def pre_process_match(self, raw_transaction: RawTransaction) -> RawTransaction:
        if self.config.multiline_config.multiline_transaction_date:
            if raw_transaction.transaction_date:
                self.previous_transaction_date = raw_transaction.transaction_date
            else:
                raw_transaction.transaction_date = self.previous_transaction_date

        raw_transaction.direction = Direction.parse(raw_transaction.direction, minus=self.minus_direction)
        return raw_transaction

    def post_process_transactions(self, transactions: list[Transaction]) -> list[Transaction]:
        return transactions

    def process_match(self, match: RawTransaction, context: MatchContext) -> RawTransaction:
        if not (config := context.multiline_config):
            return match

        # Early exit if end of page
        if context.idx >= len(context.lines) - 1:
            return match

        if config.multiline_direction:
            match.direction = self.get_multiline_direction(context)

        if config.multiline_descriptions:
            match.description = DescriptionBuilder(context, self.pattern, config).build()

        return match

    def get_multiline_direction(self, ctx: MatchContext):
        """
        Pull direction from the next line, if it can be found on the next line.

        e.g.
        Date                           Description                            Amount
        ----------------------------------------------------------------------------
        24.02.25                       PAYMENT RECEIVED - THANK YOU            79.99
                                                                                  CR

        In this case, the direction will resolve to Direction.CREDIT.

        The next line must consist *only* of a marker; anything else is a
        continuation of the statement body and leaves the direction unset.
        """
        next_line = ctx.lines[ctx.idx + 1].strip()
        if match := re.fullmatch(SharedPatterns.DIRECTION, next_line):
            return Direction.parse(match.group("direction"), minus=self.minus_direction)
        return None

    @property
    def failed_safety_message(self) -> str:
        return "Safety check failed - transactions may be inaccurate"

    @cached_property
    def transactions(self) -> list[Transaction]:
        return self.get_transactions()

    @cached_property
    def date_resolver(self) -> DateResolver:
        return DateResolver(self.pages, self.config, self.file_path)

    @cached_property
    def statement_date(self) -> datetime:
        return self.date_resolver.resolve()

    @cached_property
    def period_start(self) -> datetime | None:
        """The statement's period-start date, or None if not configured/found."""
        return self.date_resolver.resolve_period_start()

    @cached_property
    def account_resolver(self) -> AccountResolver:
        return AccountResolver(self.pages, self.config)

    @cached_property
    def currency_resolver(self) -> CurrencyResolver:
        return CurrencyResolver(self.pages, self.config)

    @abstractmethod
    def perform_safety_check(self) -> bool:
        """Validate that the extracted transactions reconcile against the statement."""

    def get_all_numbers_from_document(self) -> set[float]:
        """
        Iterate over each page in a statement, and retrieves all decimal numbers in each page.

        This is used by child classes with implementations of perform_safety_check().
        """
        extractor = NumberExtractor(self.pages)
        return extractor.get_all_numbers()


class SafetyCheckError(Exception):
    """Raised if safety check fails."""
