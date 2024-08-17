import logging
import re
from functools import lru_cache

from monopoly.constants import EntryType
from monopoly.statements.transaction import TransactionMatch

from .base import BaseStatement, SafetyCheckError

logger = logging.getLogger(__name__)


class DebitStatement(BaseStatement):
    """
    A dataclass representation of a debit statement
    """

    statement_type = EntryType.DEBIT

    def pre_process_match(
        self, transaction_match: TransactionMatch
    ) -> TransactionMatch:
        """
        Pre-processes transactions by adding a debit or credit suffix to the group dict
        """
        if self.config.has_withdraw_deposit_column:
            transaction_match.groupdict.suffix = self.get_debit_suffix(
                transaction_match
            )
        return transaction_match

    def get_debit_suffix(self, transaction_match: TransactionMatch) -> str | None:
        """
        Gets the accounting suffix for debit card statements

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
        return transaction_match.groupdict.suffix

    @lru_cache
    def get_withdrawal_pos(self, page_number: int) -> int | None:
        return self.get_column_pos("withdraw", page_number=page_number)

    @lru_cache
    def get_deposit_pos(self, page_number: int) -> int | None:
        return self.get_column_pos("deposit", page_number=page_number)

    @lru_cache
    def get_column_pos(self, column_type: str, page_number: int) -> int | None:
        pattern = re.compile(rf"{column_type}[\w()$]*", re.IGNORECASE)
        if match := pattern.search(self.header):
            return self.get_header_pos(match.group(), page_number)
        logger.warning(f"`{column_type}` column not found in header")
        return None

    @lru_cache
    def get_header_pos(self, column_name: str, page_number: int) -> int:
        """
        Returns position of the 'WITHDRAWAL' or 'DEPOSIT' header on a bank statement
        for a particular page.

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
        pages = list(self.pages)
        lines = pages[page_number].lines
        for line in lines:
            header_start_pos = line.lower().find(column_name)
            if header_start_pos == -1:
                continue
            return header_start_pos + len(column_name)

        raise ValueError(
            f"Debit header {column_name} cannot be found on page {page_number}"
        )

    @lru_cache
    def perform_safety_check(self) -> bool:
        """
        Checks that debit and credit transaction sums
        exist as a number within the statement
        """
        transactions = self.transactions

        numbers = self.get_all_numbers_from_document()

        # add a zero, for cases where the debit statement
        # either is completely debit or credit transactions
        numbers.update([0])

        debit_amounts = [
            transaction.amount for transaction in transactions if transaction.amount > 0
        ]
        credit_amounts = [
            transaction.amount for transaction in transactions if transaction.amount < 0
        ]

        debit_sum = round(abs(sum(debit_amounts)), 2)
        credit_sum = round(abs(sum(credit_amounts)), 2)

        result = all([debit_sum in numbers, credit_sum in numbers])
        if not result:
            raise SafetyCheckError(self.failed_safety_message)

        return result
