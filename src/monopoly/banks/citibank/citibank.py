import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import PdfConfig, StatementConfig
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier

logger = logging.getLogger(__name__)


class Citibank(BankBase):
    name = BankNames.CITIBANK

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(r"Statement\sDate\s+(.*)"),
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        transaction_date_format="%d %b",
        prev_balance_pattern=StatementBalancePatterns.CITIBANK,
        transaction_pattern=CreditTransactionPatterns.CITIBANK,
        filename_fallback_pattern=re.compile(r"_([A-Za-z]{3})(\d{4})"),
    )

    pdf_config = PdfConfig(
        remove_vertical_text=True,
    )

    identifiers = [
        [
            MetadataIdentifier(
                creator="Ricoh Americas Corporation, AFP2PDF",
                producer="Ricoh Americas Corporation, AFP2PDF",
            )
        ]
    ]

    statement_configs = [credit]
