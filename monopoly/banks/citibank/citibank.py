import logging

from monopoly.config import PdfConfig, StatementConfig, settings
from monopoly.constants import (
    AccountType,
    BankNames,
    MetadataIdentifier,
    TransactionPatterns,
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class Citibank(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.CITIBANK,
        account_type=AccountType.CREDIT,
        transaction_pattern=TransactionPatterns.CITIBANK,
        cashback_key=r"CASH REBATE",
        transaction_date_format="%d %b",
        statement_date_pattern=r"Statement\sDate\s+(.*)",
        statement_date_format=r"%B %d, %Y",
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
