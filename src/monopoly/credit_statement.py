import logging
import re
from functools import cached_property

from monopoly.config import CreditStatementConfig
from monopoly.constants import AccountType, StatementFields
from monopoly.pdf import PdfPage
from monopoly.statement import Statement, Transaction

logger = logging.getLogger(__name__)


class CreditStatement(Statement):
    """
    A dataclass representation of a credit statement
    """

    def __init__(
        self,
        pages: list[PdfPage],
        credit_config: CreditStatementConfig,
    ):
        super().__init__(pages, credit_config, debit_config=None)

    @cached_property
    def prev_month_balance(self) -> Transaction | None:
        """
        Returns the previous month's statement balance as a transaction,
        if it exists in the statement.

        The date is later replaced with a more accurate date by the statement processor.
        """
        if prev_balance_pattern := self.credit_config.prev_balance_pattern:
            raw_text = self.pages[0].raw_text + self.pages[1].raw_text
            if match := re.search(prev_balance_pattern, raw_text):
                groupdict = match.groupdict()
                groupdict[StatementFields.TRANSACTION_DATE] = "1900-01-01"
                return Transaction(**groupdict)  # type: ignore
            logger.debug("Unable to find previous month's balance")
        return None

    @cached_property
    def account_type(self) -> str:
        return AccountType.CREDIT

    def _inject_prev_month_balance(self, transactions: list[Transaction]):
        """
        Injects the previous month's balance as a transaction, if it exists
        """
        if self.prev_month_balance:
            first_transaction_date = transactions[0].transaction_date
            self.prev_month_balance.transaction_date = first_transaction_date
            transactions.insert(0, self.prev_month_balance)
        return transactions

    @cached_property
    def transactions(self) -> list[Transaction]:
        transactions = self._inject_prev_month_balance(super().transactions)
        return transactions
