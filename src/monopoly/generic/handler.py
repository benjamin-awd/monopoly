import logging
from functools import cached_property
from re import compile as regex
from typing import ClassVar

from monopoly.banks import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import EntryType, InternalBankNames
from monopoly.handler import StatementHandler
from monopoly.pdf import PdfParser

from .generic import DatePatternAnalyzer

logger = logging.getLogger(__name__)


class GenericBank(BankBase):
    identifiers: ClassVar[list] = []
    statement_configs: ClassVar[list[StatementConfig]] = []
    name = InternalBankNames.GENERIC
    """
    Empty bank class with variables that can be populated by
    the `GenericStatementHandler` class
    """


class GenericStatementHandler(StatementHandler):
    def __init__(self, parser: PdfParser):
        bank = parser.bank
        pages = parser.pages
        metadata = parser.metadata_identifier

        self.analyzer = DatePatternAnalyzer(pages, metadata)
        bank.statement_configs = list(filter(None, [self.debit, self.credit]))
        super().__init__(parser)

    # override get_header and ignore passed config, since
    # the header line has already been found
    def get_header(self, _: StatementConfig):
        return self.header_pattern

    @cached_property
    def debit(self):
        if self.statement_type == EntryType.DEBIT:
            logger.debug("Creating debit statement config")

            return StatementConfig(
                statement_type=EntryType.DEBIT,
                transaction_pattern=self.transaction_pattern,
                statement_date_pattern=self.statement_date_pattern,
                multiline_config=MultilineConfig(self.multiline_descriptions),
                header_pattern=regex(self.header_pattern),
            )
        return None

    @cached_property
    def credit(self):
        if self.statement_type == EntryType.CREDIT:
            logger.debug("Creating credit statement config")

            return StatementConfig(
                statement_type=EntryType.CREDIT,
                prev_balance_pattern=self.prev_balance_pattern,
                transaction_pattern=self.transaction_pattern,
                statement_date_pattern=self.statement_date_pattern,
                header_pattern=regex(self.header_pattern),
                multiline_config=MultilineConfig(self.multiline_descriptions),
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
    def multiline_descriptions(self):
        return self.analyzer.check_if_multiline()

    @cached_property
    def header_pattern(self):
        lines = self.analyzer.lines_before_first_transaction
        return self.analyzer.get_debit_statement_header_line(lines)

    @cached_property
    def prev_balance_pattern(self):
        return self.analyzer.create_previous_balance_regex()
