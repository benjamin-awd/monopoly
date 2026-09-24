import logging
import re
from collections.abc import Iterable
from functools import cached_property
from typing import ClassVar

from monopoly.banks import BankBase
from monopoly.config import Candidate, DateOrder, MultilineConfig, PdfConfig, StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfParser

from .generic import DatePatternAnalyzer

logger = logging.getLogger(__name__)


class GenericBank(BankBase):
    identifiers: ClassVar[list] = []
    statement_configs: ClassVar[list[StatementConfig]] = []
    name = "generic"
    pdf_config = PdfConfig(remove_vertical_text=True)
    """Bank with no fixed config: it is synthesised per document by GenericConfigBuilder."""

    @classmethod
    def statement_candidates(cls, parser: PdfParser) -> Iterable[Candidate]:
        return GenericConfigBuilder(parser).candidates()


class GenericConfigBuilder:
    """Synthesise a statement config, and its header, from the detected date pattern."""

    def __init__(self, parser: PdfParser):
        self.analyzer = DatePatternAnalyzer(parser.pages, parser.metadata_identifier)

    def candidates(self) -> list[Candidate]:
        # the header line was already found while analysing the document, so it
        # is paired with the config directly rather than searched for again
        return [(config, self._raw_header) for config in (self.debit, self.credit) if config]

    @cached_property
    def _date_order(self):
        pattern_name = self.analyzer.pattern.name
        if pattern_name.startswith(("mm_", "mmm_")):
            return DateOrder("MDY")
        return DateOrder("DMY")

    @cached_property
    def debit(self):
        if self.statement_type == EntryType.DEBIT:
            logger.debug("Creating debit statement config")

            return StatementConfig(
                statement_type=EntryType.DEBIT,
                transaction_pattern=self.transaction_pattern,
                statement_date_pattern=self.statement_date_pattern,
                multiline_config=MultilineConfig(self.multiline_descriptions),
                header_pattern=re.compile(self._header_regex),
                transaction_date_order=self._date_order,
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
                header_pattern=re.compile(self._header_regex),
                multiline_config=MultilineConfig(self.multiline_descriptions),
                transaction_date_order=self._date_order,
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
    def _header_result(self):
        lines = self.analyzer.lines_before_first_transaction
        return self.analyzer.get_debit_statement_header_line(lines)

    @cached_property
    def _raw_header(self):
        if self._header_result:
            return self._header_result[0].lower()
        return ""

    @cached_property
    def _header_regex(self):
        if self._header_result:
            return self._header_result[1]
        # fallback: match the first line of any page (will always match something)
        return ".*"

    @cached_property
    def prev_balance_pattern(self):
        return self.analyzer.create_previous_balance_regex()
