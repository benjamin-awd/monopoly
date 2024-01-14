import logging
import re
from functools import cached_property
from typing import Any

import fitz

from monopoly.config import CreditStatementConfig
from monopoly.constants import AccountType, StatementFields
from monopoly.pdf import PdfPage

from .base import BaseStatement, SafetyCheckError, Transaction

logger = logging.getLogger(__name__)


class CreditStatement(BaseStatement):
    """
    A dataclass representation of a credit statement
    """

    def __init__(
        self,
        document: fitz.Document,
        pages: list[PdfPage],
        credit_config: CreditStatementConfig,
    ):
        self.config = credit_config
        self.statement_type = AccountType.CREDIT
        super().__init__(document, pages, credit_config)

    @cached_property
    def prev_month_balance(self) -> list[Transaction]:
        """
        Returns the previous month's statement balance as a transaction,
        if it exists in the statement.

        The date is later replaced with a more accurate date by the statement processor.
        """
        prev_balances = []
        if prev_balance_pattern := self.config.prev_balance_pattern:
            raw_text = "".join(page.raw_text for page in self.pages)
            matches = re.finditer(prev_balance_pattern, raw_text)

            for match in matches:
                groupdict: dict[str, Any] = match.groupdict()
                groupdict[StatementFields.TRANSACTION_DATE] = "1900-01-01"
                prev_balances.append(Transaction(**groupdict))

        return prev_balances

    @cached_property
    def account_type(self) -> str:
        return AccountType.CREDIT

    def _inject_prev_month_balance(self, transactions: list[Transaction]):
        """
        Injects the previous month's balance as a transaction, if it exists
        """
        if self.prev_month_balance:
            first_transaction_date = transactions[0].transaction_date
            for prev_month_balance in self.prev_month_balance:
                prev_month_balance.transaction_date = first_transaction_date
                transactions.insert(0, prev_month_balance)
        return transactions

    @cached_property
    def transactions(self) -> list[Transaction]:
        transactions = self._inject_prev_month_balance(super().transactions)
        return transactions

    def perform_safety_check(self) -> bool:
        """Checks that the total sum of all transactions is present
        somewhere within the document

        Text is re-extracted from the page, as some bank-specific bounding-box
        configurations (e.g. HSBC) may preclude the total from being extracted

        Returns `False` if the total does not exist in the document.
        """
        df = self.df
        amount = StatementFields.AMOUNT
        numbers = self.get_all_numbers_from_document()

        total_amount = abs(round(df[amount].sum(), 2))

        result = total_amount in numbers
        if not result:
            raise SafetyCheckError(
                f"Total amount {total_amount} cannot be found in credit statement"
            )

        return result
