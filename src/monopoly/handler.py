import logging
from functools import cached_property

from monopoly.config import StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfParser
from monopoly.statements import BaseStatement, CreditStatement, DebitStatement

logger = logging.getLogger(__name__)


class StatementHandler:
    """
    Retrieves statement information like transactions from the PDF,
    and identifies the statement as either a debit or credit statement
    based on the debit and credit config.
    """

    def __init__(self, parser: PdfParser):
        self.parser = parser
        self.bank = parser.bank

    @property
    def transactions(self):
        return self.statement.transactions

    @property
    def statement_date(self):
        return self.statement.statement_date

    def get_header(self, config: StatementConfig) -> str | None:
        pattern = config.header_pattern

        pages = self.parser.get_pages()
        for page in pages:
            for line in page.lines:
                if match := pattern.search(line):
                    return match.group().lower()
        return None

    def perform_safety_check(self):
        self.statement.perform_safety_check()

    @cached_property
    def statement(self) -> BaseStatement:
        parser = self.parser

        for config in self.bank.statement_configs:
            if header := self.get_header(config):
                match config.statement_type:
                    case EntryType.DEBIT:
                        logger.debug("Statement type detected: %s", EntryType.DEBIT)
                        return DebitStatement(parser, config, header)
                    case EntryType.CREDIT:
                        logger.debug("Statement type detected: %s", EntryType.CREDIT)
                        return CreditStatement(parser, config, header)

        raise RuntimeError("Could not create statement object")
