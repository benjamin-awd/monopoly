import logging
from functools import cached_property

from monopoly.config import StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfParser
from monopoly.statements import BaseStatement, CreditStatement, DebitStatement, MissingHeaderError

logger = logging.getLogger(__name__)

STATEMENT_CLASSES: dict[EntryType, type[BaseStatement]] = {
    EntryType.DEBIT: DebitStatement,
    EntryType.CREDIT: CreditStatement,
}


class StatementHandler:
    """
    Retrieve statement information like transactions from the PDF.

    Identifies the statement as either a debit or credit statement based on the debit and credit config.
    """

    def __init__(self, parser: PdfParser):
        self.bank = parser.bank
        self.pages = parser.pages
        self.file_path = parser.file_path

    @property
    def statement_configs(self) -> list[StatementConfig]:
        """The configs to try, in order. Subclasses may synthesise their own."""
        return self.bank.statement_configs

    def get_header(self, config: StatementConfig) -> str | None:
        pattern = config.header_pattern

        for page in self.pages:
            for line in page.lines:
                if match := pattern.search(line):
                    return match.group().lower()
        return None

    @cached_property
    def statement(self):
        return self._get_statement()

    def _get_statement(self) -> BaseStatement:
        for config in self.statement_configs:
            if header := self.get_header(config):
                logger.debug("Statement type detected: %s", config.statement_type)
                statement_class = STATEMENT_CLASSES[config.statement_type]
                return statement_class(self.pages, self.bank.name, config, header, self.file_path)

        msg = "Could not find header in statement"
        raise MissingHeaderError(msg)
