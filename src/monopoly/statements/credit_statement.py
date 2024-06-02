import logging
import re

from monopoly.config import CreditStatementConfig
from monopoly.constants import EntryType
from monopoly.statements.transaction import Transaction, TransactionGroupDict

from .base import BaseStatement, SafetyCheckError

logger = logging.getLogger(__name__)


class CreditStatement(BaseStatement):
    """
    A dataclass representation of a credit statement
    """

    statement_type = EntryType.CREDIT

    def post_process_transactions(self, transactions) -> list[Transaction]:
        previous_month_balances = self.get_prev_month_balances()
        if previous_month_balances:
            first_transaction_date = next(iter(transactions)).date
            for prev_month_balance in previous_month_balances:
                groupdict = TransactionGroupDict(**prev_month_balance.groupdict())
                groupdict.transaction_date = first_transaction_date
                prev_month_transaction = Transaction(**groupdict)
                transactions.insert(0, prev_month_transaction)
        return transactions

    def get_prev_month_balances(self) -> list[re.Match]:
        """
        Returns the previous month's statement balance as a transaction,
        if it exists in the statement.

        The date is later replaced with a more accurate date by the statement handler.
        """
        prev_balances = []

        if isinstance(self.config, CreditStatementConfig):
            if pattern := self.config.prev_balance_pattern:
                for page in self.pages:
                    for line in page.lines:
                        match = pattern.search(line)
                        if match:
                            prev_balances.append(match)

        return prev_balances

    def perform_safety_check(self) -> bool:
        """Checks that the total sum of all transactions is present
        somewhere within the document

        Text is re-extracted from the page, as some bank-specific bounding-box
        configurations (e.g. HSBC) may preclude the total from being extracted

        Returns `False` if the total does not exist in the document.
        """
        numbers = self.get_all_numbers_from_document()
        transactions = self.transactions

        amounts = [transaction.amount for transaction in transactions]
        total_amount = abs(round(sum(amounts), 2))

        result = total_amount in numbers
        if not result:
            raise SafetyCheckError(
                f"Total amount {total_amount} cannot be found in credit statement"
            )

        return result
