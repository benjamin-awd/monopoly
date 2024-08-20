import logging

from monopoly.config import PdfConfig, StatementConfig
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Citibank(BankBase):
    credit_config = StatementConfig(
        statement_type=EntryType.CREDIT,
        bank_name=BankNames.CITIBANK,
        statement_date_pattern=r"Statement\sDate\s+(.*)",
        header_pattern=r"(DATE.*DESCRIPTION.*AMOUNT)",
        prev_balance_pattern=StatementBalancePatterns.CITIBANK,
        transaction_pattern=CreditTransactionPatterns.CITIBANK,
    )

    pdf_config = PdfConfig(
        page_bbox=(20, 0, 595, 840),
        page_range=(0, -3),
    )

    identifiers = [
        [
            MetadataIdentifier(
                creator="Ricoh Americas Corporation, AFP2PDF",
                producer="Ricoh Americas Corporation, AFP2PDF",
            )
        ]
    ]

    statement_configs = [credit_config]
