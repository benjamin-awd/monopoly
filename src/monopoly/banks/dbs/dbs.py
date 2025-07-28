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
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class Dbs(BankBase):
    name = BankNames.DBS

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MMM_YYYY,
        header_pattern=regex(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        transaction_date_format="%d %b",
        transaction_pattern=CreditTransactionPatterns.DBS,
        prev_balance_pattern=StatementBalancePatterns.DBS,
    )

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=ISO8601.DD_MMM_YYYY,
        multiline_config=MultilineConfig(multiline_descriptions=True),
        header_pattern=regex(r"(WITHDRAWAL.*DEPOSIT.*BALANCE)"),
        transaction_date_format="%d %b",
        transaction_pattern=DebitTransactionPatterns.DBS,
    )

    consolidated = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=regex(rf"Details as at {ISO8601.DD_MMM_YYYY}"),
        multiline_config=MultilineConfig(multiline_descriptions=True),
        header_pattern=regex(r"(\s*Date\s+Description\s+Withdrawal \(-\).*)"),
        transaction_date_format="%d %b",
        transaction_pattern=DebitTransactionPatterns.DBS_POSB_CONSOLIDATED,
        transaction_bound=220,
    )

    identifiers = [
        # 2023-present
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="Quadient CXM AG"),
        ],
        # 2021-2022
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="Quadient Group AG"),
        ],
        # 2018-2020
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(producer="StreamServe Communication Server"),
        ],
    ]

    statement_configs = [credit, consolidated, debit]
