import logging
from re import compile as regex

from monopoly.banks.base import BankBase
from monopoly.config import StatementConfig
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
        statement_date_pattern=regex(r"Statement\sDate\s+(.*)"),
        header_pattern=regex(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        prev_balance_pattern=StatementBalancePatterns.CITIBANK,
        transaction_pattern=CreditTransactionPatterns.CITIBANK,
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
