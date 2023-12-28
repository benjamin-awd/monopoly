import logging

from monopoly.config import CreditStatementConfig, PdfConfig, settings
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    MetadataIdentifier,
    StatementBalancePatterns,
)

from ..base import ProcessorBase

logger = logging.getLogger(__name__)


class Citibank(ProcessorBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.CITIBANK,
        statement_date_pattern=r"Statement\sDate\s+(.*)",
        statement_date_format=r"%B %d, %Y",
        prev_balance_pattern=StatementBalancePatterns.CITIBANK,
        transaction_pattern=CreditTransactionPatterns.CITIBANK,
        transaction_date_format="%d %b",
    )

    pdf_config = PdfConfig(
        passwords=settings.citibank_pdf_passwords,
        page_bbox=(20, 0, 595, 840),
        page_range=(0, -3),
    )

    identifiers = [
        MetadataIdentifier(
            creator="Ricoh Americas Corporation, AFP2PDF",
            producer="Ricoh Americas Corporation, AFP2PDF",
        )
    ]
