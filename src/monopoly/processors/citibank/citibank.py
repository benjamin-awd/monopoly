import logging

from monopoly.config import PdfConfig, StatementConfig, TransactionConfig, settings
from monopoly.constants import (
    AccountType,
    BankNames,
    MetadataIdentifier,
    StatementBalancePatterns,
    TransactionPatterns,
)

from ..base import ProcessorBase

logger = logging.getLogger(__name__)


class Citibank(ProcessorBase):
    statement_config = StatementConfig(
        bank_name=BankNames.CITIBANK,
        account_type=AccountType.CREDIT,
        date_pattern=r"Statement\sDate\s+(.*)",
        date_format=r"%B %d, %Y",
        prev_balance_pattern=StatementBalancePatterns.CITIBANK,
    )

    transaction_config = TransactionConfig(
        pattern=TransactionPatterns.CITIBANK,
        date_format="%d %b",
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
