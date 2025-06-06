import logging
from re import compile as regex

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier

logger = logging.getLogger(__name__)


class Maybank(BankBase):
    name = BankNames.MAYBANK

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=regex(rf"(?:結單日期)[:\s]+{ISO8601.DD_MM_YY}"),
        header_pattern=regex(r"(DATE.*DESCRIPTION.*AMOUNT.*BALANCE)"),
        transaction_pattern=DebitTransactionPatterns.MAYBANK,
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MMM_YY,
        header_pattern=regex(r"(Date.*Description.*Amount)"),
        transaction_pattern=CreditTransactionPatterns.MAYBANK,
        prev_balance_pattern=StatementBalancePatterns.MAYBANK,
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    identifiers = [
        [
            MetadataIdentifier(
                author="Maybank2U.com",
                creator="Maybank2u.com",
                producer="iText",
            ),
        ],
        [
            MetadataIdentifier(
                title="Credit Card Statement",
                author="Maybank2U.com",
                producer="iText",
            ),
        ],
    ]

    statement_configs = [credit, debit]
