import logging
import re
from functools import cached_property

from monopoly.constants import EntryType
from monopoly.statements.transaction import TransactionMatch

from .base import BaseStatement, SafetyCheckError

logger = logging.getLogger(__name__)


class DebitStatement(BaseStatement):
    """
    A dataclass representation of a debit statement
    """

    statement_type = EntryType.DEBIT

    @cached_property
    def debit_header(self):
        """Checks if the statement is a debit statement"""
        identifier = self.config.debit_statement_identifier
        for page in self.pages:
            for line in page.lines:
                if re.search(identifier, line):
                    return line.lower()
        return None

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
        if self.withdrawal_pos and self.deposit_pos:
            amount = transaction_match.groupdict.amount
            line: str = transaction_match.match.string
            start_pos = line.find(amount)
            # assume that numbers are right aligned
            end_pos = start_pos + len(amount) - 1
            withdrawal_diff = abs(end_pos - self.withdrawal_pos)
            deposit_diff = abs(end_pos - self.deposit_pos)
            if withdrawal_diff > deposit_diff:
                return "CR"
            return "DR"
        return transaction_match.groupdict.suffix

    @cached_property
    def withdrawal_pos(self) -> int | None:
        return self.get_column_pos("withdraw")

    @cached_property
    def deposit_pos(self) -> int | None:
        return self.get_column_pos("deposit")

    def get_column_pos(self, column_type: str) -> int | None:
        pattern = re.compile(rf"{column_type}[\w()$]*", re.IGNORECASE)
        match: re.Match | None = pattern.search(self.debit_header)
        if match:
            return self.get_header_pos(match.group())
        logger.warning(f"`{column_type}` column not found in header")
        return None

    def get_header_pos(self, column_name: str) -> int:
        """
        Returns position of the 'WITHDRAWAL' or 'DEPOSIT' header on a bank statement

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
        if self.debit_header:
            result = self.debit_header.find(column_name) + len(column_name)
            return result

        raise ValueError(f"Debit header {column_name} missing in {self.debit_header}")

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
