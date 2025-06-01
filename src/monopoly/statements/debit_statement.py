import logging
import re

from monopoly.constants import EntryType
from monopoly.statements.transaction import TransactionMatch

from .base import BaseStatement, SafetyCheckError

logger = logging.getLogger(__name__)


class DebitStatement(BaseStatement):
    """A dataclass representation of a debit statement."""

    statement_type = EntryType.DEBIT

    def pre_process_match(self, transaction_match: TransactionMatch) -> TransactionMatch:
        """Pre-process transactions by adding a debit or credit polarity identifier to the group dict."""
        if self.config.statement_type == EntryType.DEBIT:
            transaction_match.groupdict.polarity = self.get_debit_polarity(transaction_match)
        return transaction_match

    def get_debit_polarity(self, transaction_match: TransactionMatch) -> str | None:
        """
        Get the accounting polarity for debit card statements.

        Attempts to identify whether a transaction is a debit
        or credit entry based on the distance from the withdrawal
        or deposit columns.
        """
        page_number = transaction_match.page_number
        withdrawal_pos = self.get_withdrawal_pos(page_number)
        deposit_pos = self.get_deposit_pos(page_number)

        if deposit_pos and withdrawal_pos:
            amount = transaction_match.groupdict.amount
            line: str = transaction_match.match.string
            start_pos = line.find(amount)
            # assume that numbers are right aligned
            end_pos = start_pos + len(amount) - 1
            withdrawal_diff = abs(end_pos - withdrawal_pos)
            deposit_diff = abs(end_pos - deposit_pos)
            if withdrawal_diff > deposit_diff:
                return "CR"
            return "DR"
        return transaction_match.groupdict.polarity

    def get_withdrawal_pos(self, page_number: int) -> int | None:
        common_names = ["withdraw", "debit"]
        for name in common_names:
            if pos := self.get_column_pos(name, page_number=page_number):
                return pos
        logger.debug("%s column not found in header on page %s", common_names, page_number)
        return False

    def get_deposit_pos(self, page_number: int) -> int | None:
        common_names = ["deposit", "credit"]
        for name in common_names:
            if pos := self.get_column_pos(name, page_number=page_number):
                return pos
        logger.debug("%s column not found in header on page %s", common_names, page_number)
        return False

    def get_column_pos(self, column_type: str, page_number: int) -> int | None:
        pattern = re.compile(rf"{column_type}[\w()$]*", re.IGNORECASE)
        if match := pattern.search(self.header):
            return self.get_header_pos(match.group(), page_number)
        return None

    def get_header_pos(self, column_name: str, page_number: int) -> int:
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
        return -1

    def perform_safety_check(self: BaseStatement) -> bool:
        """Check that debit and credit transaction sums exist as a number within the statement."""
        transactions = self.transactions

        numbers = self.get_all_numbers_from_document()

        # add a zero, for cases where the debit statement
        # either is completely debit or credit transactions
        numbers.update([0])

        debit_amounts = [transaction.amount for transaction in transactions if transaction.amount > 0]
        credit_amounts = [transaction.amount for transaction in transactions if transaction.amount < 0]

        debit_sum = round(abs(sum(debit_amounts)), 2)
        credit_sum = round(abs(sum(credit_amounts)), 2)

        result = all([debit_sum in numbers, credit_sum in numbers])
        if not result:
            raise SafetyCheckError(self.failed_safety_message)

        return result
