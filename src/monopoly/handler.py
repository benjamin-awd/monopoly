import logging
import re

from monopoly.config import CreditStatementConfig, DebitStatementConfig, StatementConfig
from monopoly.pdf import PdfParser
from monopoly.statements import CreditStatement, DebitStatement

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
        self.statement = self.get_statement()

    @property
    def transactions(self):
        return self.statement.transactions

    @property
    def statement_date(self):
        return self.statement.statement_date

    def get_header(self, config: StatementConfig) -> str | None:
        header_pattern = re.compile(config.header_pattern)
        pages = self.parser.get_pages()
        for page in pages:
            for line in page.lines:
                if match := header_pattern.search(line):
                    return match.group().lower()
        return None

    def perform_safety_check(self):
        self.statement.perform_safety_check()

    def get_statement(self) -> CreditStatement | DebitStatement:
        parser = self.parser
        bank = parser.bank

        statement_factory = {
            DebitStatementConfig: DebitStatement,
            CreditStatementConfig: CreditStatement,
        }

        configs = filter(None, [bank.debit_config, bank.credit_config])

        for config in configs:
            if header := self.get_header(config):
                statement_cls = statement_factory[type(config)]
                return statement_cls(parser, config, header)

        raise RuntimeError("Could not create statement object")
