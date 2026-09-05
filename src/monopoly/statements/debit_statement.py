import logging
import re
from functools import cached_property

from monopoly.constants import Direction, EntryType
from monopoly.statements.column_layout import ColumnLayout
from monopoly.statements.safety import sums_reconcile
from monopoly.statements.transaction import RawTransaction

from .base import BaseStatement, SafetyCheckError

logger = logging.getLogger(__name__)


class DebitStatement(BaseStatement):
    """A dataclass representation of a debit statement."""

    statement_type = EntryType.DEBIT
    minus_direction = Direction.DEBIT

    def pre_process_match(self, raw_transaction: RawTransaction) -> RawTransaction:
        """Pre-process transactions by adding a debit or credit direction identifier to the group dict."""
        raw_transaction = super().pre_process_match(raw_transaction)
        direction = raw_transaction.direction

        # No explicit marker: infer from which amount column the value sits under
        if direction is None and (layout := self.column_layouts[raw_transaction.page_number]):
            direction = layout.classify(self._amount_end_pos(raw_transaction))

        raw_transaction.direction = direction or Direction.CREDIT  # default to credit
        return raw_transaction

    @cached_property
    def column_layouts(self) -> list[ColumnLayout | None]:
        """
        The withdrawal/deposit geometry of each page, indexed by page number.

        Computed once per statement. A page is `None` when either column is
        missing from it, which is the same thing as having no usable geometry —
        the two positions are only meaningful together.
        """
        layouts: list[ColumnLayout | None] = []
        for page_number in range(len(self.pages)):
            withdrawal = self.get_withdrawal_pos(page_number)
            deposit = self.get_deposit_pos(page_number)
            layouts.append(None if withdrawal is None or deposit is None else ColumnLayout(withdrawal, deposit))
        return layouts

    @staticmethod
    def _amount_end_pos(raw_transaction: RawTransaction) -> int:
        """Amounts are right-aligned, so the final character is what locates the column."""
        if raw_transaction.match is None:
            msg = "RawTransaction.match is required for direction detection"
            raise ValueError(msg)
        line = raw_transaction.match.string
        return line.find(raw_transaction.amount) + len(raw_transaction.amount) - 1

    def get_withdrawal_pos(self, page_number: int) -> int | None:
        common_names = ["withdraw", "debit", r"from\ your\ account"]
        for name in common_names:
            if (pos := self.get_column_pos(name, page_number=page_number)) is not None:
                return pos
        logger.debug("%s column not found in header on page %s", common_names, page_number)
        return None

    def get_deposit_pos(self, page_number: int) -> int | None:
        common_names = ["deposit", "credit", r"to\ your\ account"]
        for name in common_names:
            if (pos := self.get_column_pos(name, page_number=page_number)) is not None:
                return pos
        logger.debug("%s column not found in header on page %s", common_names, page_number)
        return None

    def get_column_pos(self, column_type: str, page_number: int) -> int | None:
        pattern = re.compile(rf"{column_type}[\w()$]*", re.IGNORECASE)
        if match := pattern.search(self.header):
            return self.get_header_pos(match.group(), page_number)
        return None

    def get_header_pos(self, column_name: str, page_number: int) -> int | None:
        """
        Return position of the 'WITHDRAWAL' or 'DEPOSIT' header for a particular page.

        An assumption is made here that numbers are right aligned, meaning
        that if an amount matches with the end of the withdrawal string position,
        the item is in fact a withdrawal

        e.g.
        ```
        DATE         DESCRIPTION          WITHDRAWAL         DEPOSIT
        15 OCT       bill payment             322.07
        16 OCT       item                                     123.12
        ```
        """
        header_pattern = self.config.header_pattern
        lines = self.pages[page_number].lines
        for line in lines:
            if match := header_pattern.search(line):
                header = match.string.lower()
                header_start_pos = header.find(column_name.lower())
                if header_start_pos == -1:
                    continue
                return header_start_pos + len(column_name)

        logger.debug("Debit header %s cannot be found on page %s", column_name, page_number)
        return None

    def perform_safety_check(self) -> bool:
        """Check that debit and credit transaction sums exist as a number within the statement."""
        # zero covers statements that are entirely debits or entirely credits
        numbers = self.get_all_numbers_from_document() | {0.0}

        if not sums_reconcile(self.transactions, numbers):
            raise SafetyCheckError(self.failed_safety_message)

        return True
