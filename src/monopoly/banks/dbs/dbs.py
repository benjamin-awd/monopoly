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
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Dbs(BankBase):
    credit_config = StatementConfig(
        statement_type=EntryType.CREDIT,
        bank_name=BankNames.DBS,
        statement_date_pattern=regex(r"(\d{2}\s[A-Za-z]{3}\s\d{4})"),
        multiline_transactions=False,
        header_pattern=regex(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        transaction_pattern=CreditTransactionPatterns.DBS,
        prev_balance_pattern=StatementBalancePatterns.DBS,
    )

    debit_config = StatementConfig(
        statement_type=EntryType.DEBIT,
        bank_name=BankNames.DBS,
        statement_date_pattern=regex(r"(\d{2}\s[A-Za-z]{3}\s\d{4})"),
        multiline_transactions=True,
        header_pattern=regex(r"(WITHDRAWAL.*DEPOSIT.*BALANCE)"),
        transaction_pattern=DebitTransactionPatterns.DBS,
    )

    identifiers = [
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="Quadient CXM AG"),
        ],
    ]

    statement_configs = [debit_config, credit_config]
