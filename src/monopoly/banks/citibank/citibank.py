import logging

from monopoly.config import PdfConfig, StatementConfig, TransactionConfig, settings
from monopoly.constants import (
    AccountType,
    BankNames,
    MetadataIdentifier,
    TransactionPatterns,
    StatementBalancePatterns
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class Citibank(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.CITIBANK,
        account_type=AccountType.CREDIT,
        statement_date_pattern=r"Statement\sDate\s+(.*)",
        statement_date_format=r"%B %d, %Y",
        prev_balance_pattern=StatementBalancePatterns.CITIBANK,
    )

    transaction_config = TransactionConfig(
        pattern=TransactionPatterns.CITIBANK,
        date_format="%d %b",
    )

    pdf_config = PdfConfig(
        password=settings.citibank_pdf_password,
        page_bbox=(20, 0, 595, 840),
        page_range=(0, -3),
    )

    identifiers = [
        MetadataIdentifier(
            creator="Ricoh Americas Corporation, AFP2PDF",
            producer="Ricoh Americas Corporation, AFP2PDF",
        )
    ]
