from monopoly.pdf import PdfParser
from monopoly.statements import CreditStatement, DebitStatement


class StatementHandler:
    """
    Retrieves statement information like transactions from the PDF,
    and identifies the statement as either a debit or credit statement
    based on the debit and credit config.
    """

    def __init__(self, parser: PdfParser):
        self.parser = parser
        self.bank = parser.bank
        self.statement = self.get_statement(self.parser)

    @property
    def transactions(self):
        return self.statement.transactions

    @property
    def statement_date(self):
        return self.statement.statement_date

    def perform_safety_check(self):
        self.statement.perform_safety_check()

    @classmethod
    def get_statement(cls, parser: PdfParser) -> CreditStatement | DebitStatement:
        bank = parser.bank

        if bank.debit_config:
            debit_statement = DebitStatement(parser, bank.debit_config)
            if debit_statement.debit_header:
                return debit_statement

        if not bank.credit_config:
            raise RuntimeError("Missing credit config")

        # if it's not a debit statement, assume that it's a credit statement
        return CreditStatement(parser, bank.credit_config)
