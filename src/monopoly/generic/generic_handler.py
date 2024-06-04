import logging
from functools import cached_property

from monopoly.banks import BankBase
from monopoly.config import CreditStatementConfig, DebitStatementConfig
from monopoly.constants import EntryType, InternalBankNames
from monopoly.handler import StatementHandler
from monopoly.pdf import PdfParser

from .generic import DatePatternAnalyzer

logger = logging.getLogger(__name__)


class GenericBank(BankBase):
    """
    Empty bank class with variables that can be populated by
    the `GenericStatementHandler` class
    """

    def __init__(self):
        super().__init__(generic=True)

    @property
    def identifiers(self):
        return None


class GenericStatementHandler(StatementHandler):
    def __init__(self, parser: PdfParser):
        pages = parser.get_pages()
        self.analyzer = DatePatternAnalyzer(pages)
        parser.bank.debit_config = self.debit_config
        parser.bank.credit_config = self.credit_config
        super().__init__(parser)

    @cached_property
    def debit_config(self):
        if self.statement_type == EntryType.DEBIT:
            logger.debug("Creating debit statement config")

            return DebitStatementConfig(
                bank_name=InternalBankNames.GENERIC,
                transaction_pattern=self.transaction_pattern,
                statement_date_pattern=self.statement_date_pattern,
                multiline_transactions=self.multiline_transactions,
                debit_statement_identifier=self.debit_statement_identifier,
            )
        return None

    @cached_property
    def credit_config(self):
        if self.statement_type == EntryType.CREDIT:
            logger.debug("Creating credit statement config")

            return CreditStatementConfig(
                bank_name=InternalBankNames.GENERIC,
                prev_balance_pattern=self.prev_balance_pattern,
                transaction_pattern=self.transaction_pattern,
                statement_date_pattern=self.statement_date_pattern,
                multiline_transactions=self.multiline_transactions,
            )
        return None

    @cached_property
    def transaction_pattern(self):
        return self.analyzer.create_transaction_pattern()

    @cached_property
    def statement_type(self):
        return self.analyzer.get_statement_type()

    @cached_property
    def statement_date_pattern(self):
        return self.analyzer.create_statement_date_pattern()

    @cached_property
    def multiline_transactions(self):
        return self.analyzer.check_if_multiline()

    @cached_property
    def debit_statement_identifier(self):
        return self.analyzer.get_debit_statement_header_line()

    @cached_property
    def prev_balance_pattern(self):
        return self.analyzer.create_previous_balance_regex()
