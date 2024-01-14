import logging
import re
from functools import cached_property

import fitz

from monopoly.config import DebitStatementConfig
from monopoly.constants import AccountType, StatementFields
from monopoly.pdf import PdfPage

from .base import BaseStatement, Transaction

logger = logging.getLogger(__name__)


class DebitStatement(BaseStatement):
    """
    A dataclass representation of a debit statement
    """

    def __init__(
        self,
        document: fitz.Document,
        pages: list[PdfPage],
        debit_config: DebitStatementConfig,
    ):
        self.config = debit_config
        self.statement_type = AccountType.DEBIT
        super().__init__(document, pages, debit_config)

    def _process_line(
        self,
        line: str,
        lines: list[str],
        idx: int,
        pattern: re.Pattern,
    ) -> Transaction | None:
        if match := pattern.search(line):
            groupdict = match.groupdict()
            suffix = self.get_debit_suffix(line, pattern)

            # if the entry is a credit then add parenthesis around
            # the amount, which causes the Transaction class to
            # treat the amount as a credit / 'positive' transaction
            if suffix == "CR":
                line = line.replace(groupdict["amount"], f"({groupdict['amount']})")
                lines[idx] = line

            # continue with normal line processing
            return super()._process_line(line, lines, idx, pattern)
        return None

    def get_debit_suffix(self, line: str, pattern: re.Pattern):
        """
        Gets the accounting suffix for debit card statements

        This is necessary, since the amount in the row does not have any
        identifier apart from column position.
        """
        if match := pattern.search(line):
            amount = match[StatementFields.AMOUNT]
            pos = line.find(amount)
            withdrawal_diff = abs(pos - self.withdrawal_pos)
            deposit_diff = abs(pos - self.deposit_pos)
            if withdrawal_diff > deposit_diff:
                return "CR"
            return "DR"
        return None

    @cached_property
    def debit_header(self) -> str | None:
        if self.config and self.config.debit_statement_identifier:
            for line in self.pages[0].lines:
                if re.search(self.config.debit_statement_identifier, line):
                    return line.lower()
        return None

    @cached_property
    def withdrawal_pos(self) -> int:
        return self.get_header_pos("withdrawal")

    @cached_property
    def deposit_pos(self) -> int:
        return self.get_header_pos("deposit")

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
        result = self.debit_header.find(column_name) + len(column_name)
        if not result:
            raise ValueError(
                f"Debit header {column_name} missing in {self.debit_header}"
            )
        return result

    def perform_safety_check(self) -> bool:
        """
        Checks that debit and credit transaction sums
        exist as a number within the statement
        """
        df = self.df
        amount = StatementFields.AMOUNT

        numbers = self.get_all_numbers_from_document()

        # add a zero, for cases where the debit statement
        # either is completely debit or credit transactions
        numbers.update([0])

        debit_sum = round(abs(df[df[amount] > 0][amount].sum()), 2)
        credit_sum = round(abs(df[df[amount] < 0][amount].sum()), 2)

        result = all([debit_sum in numbers, credit_sum in numbers])

        if not result:
            logger.warning(self.warning_message)

        return result
