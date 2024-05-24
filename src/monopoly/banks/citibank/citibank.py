import logging

from monopoly.config import CreditStatementConfig, PdfConfig, passwords
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    MetadataIdentifier,
    StatementBalancePatterns,
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class Citibank(BankBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.CITIBANK,
        statement_date_pattern=r"Statement\sDate\s+(.*)",
        prev_balance_pattern=StatementBalancePatterns.CITIBANK,
        transaction_pattern=CreditTransactionPatterns.CITIBANK,
    )

    pdf_config = PdfConfig(
        page_bbox=(20, 0, 595, 840),
        page_range=(0, -3),
    )

    identifiers = [
        MetadataIdentifier(
            creator="Ricoh Americas Corporation, AFP2PDF",
            producer="Ricoh Americas Corporation, AFP2PDF",
        )
    ]

    passwords = passwords.citibank_pdf_passwords
