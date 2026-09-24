import logging
from typing import TYPE_CHECKING

from monopoly.constants import EntryType
from monopoly.statements import BaseStatement, CreditStatement, DebitStatement, MissingHeaderError

if TYPE_CHECKING:
    from monopoly.pdf import PdfParser

logger = logging.getLogger(__name__)

STATEMENT_CLASSES: dict[EntryType, type[BaseStatement]] = {
    EntryType.DEBIT: DebitStatement,
    EntryType.CREDIT: CreditStatement,
}


def select_statement(parser: "PdfParser") -> BaseStatement:
    """
    Build the statement for the first candidate config whose header was found.

    Candidates come from the bank itself (`BankBase.statement_candidates`), so
    the generic bank can synthesise its config without a special case here.
    """
    bank = parser.bank
    for config, header in bank.statement_candidates(parser):
        if header:
            logger.debug("Statement type detected: %s", config.statement_type)
            statement_class = STATEMENT_CLASSES[config.statement_type]
            return statement_class(parser.pages, bank.name, config, header, parser.file_path)

    msg = "Could not find header in statement"
    raise MissingHeaderError(msg)
