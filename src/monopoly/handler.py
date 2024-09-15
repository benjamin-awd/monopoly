import logging
from functools import lru_cache
from typing import Type

from monopoly.banks import BankBase
from monopoly.config import StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfPage
from monopoly.statements import BaseStatement, CreditStatement, DebitStatement

logger = logging.getLogger(__name__)


class StatementHandler:
    """
    Retrieves statement information like transactions from the PDF,
    and identifies the statement as either a debit or credit statement
    based on the debit and credit config.
    """

    def __init__(self, bank: Type[BankBase], pages: list[PdfPage]):
        self.bank = bank
        self.pages = pages

    def get_header(self, config: StatementConfig) -> str | None:
        pattern = config.header_pattern

        for page in self.pages:
            for line in page.lines:
                if match := pattern.search(line):
                    return match.group().lower()
        return None

    @lru_cache
    def get_statement(self) -> BaseStatement:
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

        raise RuntimeError("Could not find header in statement")
