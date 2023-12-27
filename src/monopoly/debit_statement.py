import logging
import re
from functools import cached_property

from monopoly.config import DebitStatementConfig
from monopoly.constants import StatementFields
from monopoly.pdf import PdfPage
from monopoly.statement import Statement, Transaction

logger = logging.getLogger(__name__)


class DebitStatement(Statement):
    """
    A dataclass representation of a debit statement
    """

    def __init__(
        self,
        pages: list[PdfPage],
        debit_config: DebitStatementConfig,
    ):
        super().__init__(pages, None, debit_config)  # type: ignore

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
        if self.debit_config and self.debit_config.debit_account_identifier:
            for line in self.pages[0].lines:
                if re.search(self.debit_config.debit_account_identifier, line):
                    return line.lower()
        return None

    @cached_property
    def withdrawal_pos(self) -> int:
        if self.debit_header:
            return self.debit_header.find("withdrawal")
        raise ValueError("Debit header missing")

    @cached_property
    def deposit_pos(self) -> int:
        if self.debit_header:
            return self.debit_header.find("deposit")
        raise ValueError("Debit header missing")
