import logging

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

    def perform_safety_check(self):
        self.statement.perform_safety_check()

    def get_statement(self) -> CreditStatement | DebitStatement:
        bank = self.parser.bank
        debit_config, credit_config = bank.debit_config, bank.credit_config

        if debit_config:
            debit_statement = DebitStatement(self.parser, debit_config)
            # if we can find transactions using the debit config
            # assume that it is a debit statement
            try:
                if debit_statement.get_transactions():
                    return debit_statement
            except (ValueError, TypeError) as err:
                logger.debug(
                    "Could not parse with debit config due to error: %s",
                    repr(err),
                )
            except Exception as err:  # pylint: disable=broad-exception-caught
                logger.error(
                    "Unexpected error while parsing with debit config: %s",
                    repr(err),
                )

        if not credit_config:
            raise RuntimeError(f"Missing credit config for bank: {bank}")

        # if it's not a debit statement, assume that it's a credit statement
        return CreditStatement(self.parser, credit_config)
