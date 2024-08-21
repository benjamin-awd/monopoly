import logging
from re import compile as regex

from monopoly.config import StatementConfig
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Maybank(BankBase):
    debit_config = StatementConfig(
        statement_type=EntryType.DEBIT,
        bank_name=BankNames.MAYBANK,
        statement_date_pattern=regex(r"(?:結單日期)[:\s]+(\d{2}\/\d{2}\/\d{2})"),
        header_pattern=regex(r"(DATE.*DESCRIPTION.*AMOUNT.*BALANCE)"),
        transaction_pattern=DebitTransactionPatterns.MAYBANK,
        has_withdraw_deposit_column=False,
        multiline_transactions=True,
    )

    credit_config = StatementConfig(
        statement_type=EntryType.CREDIT,
        bank_name=BankNames.MAYBANK,
        statement_date_pattern=regex(r"(\d{2}\s[A-Z]{3}\s\d{2})"),
        header_pattern=regex(r"(Date.*Description.*Amount)"),
        transaction_pattern=CreditTransactionPatterns.MAYBANK,
        prev_balance_pattern=StatementBalancePatterns.MAYBANK,
        multiline_transactions=True,
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

    statement_configs = [debit_config, credit_config]
