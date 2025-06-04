import logging
from functools import cached_property

from monopoly.config import StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfParser
from monopoly.statements import BaseStatement, CreditStatement, DebitStatement

logger = logging.getLogger(__name__)


class StatementHandler:
    """
    Retrieve statement information like transactions from the PDF.

    Identifies the statement as either a debit or credit statement based on the debit and credit config.
    """

    def __init__(self, parser: PdfParser):
        self.bank = parser.bank
        self.pages = parser.pages

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
        pages = self.pages
        bank_name = self.bank.name

        for config in self.bank.statement_configs:
            if header := self.get_header(config):
                match config.statement_type:
                    case EntryType.DEBIT:
                        logger.debug("Statement type detected: %s", EntryType.DEBIT)
                        return DebitStatement(pages, bank_name, config, header)
                    case EntryType.CREDIT:
                        logger.debug("Statement type detected: %s", EntryType.CREDIT)
                        return CreditStatement(pages, bank_name, config, header)

        msg = "Could not find header in statement"
        raise RuntimeError(msg)
