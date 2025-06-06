import logging
from re import compile as regex

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class Uob(BankBase):
    name = BankNames.UOB

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=regex(rf"Statement Date.*{ISO8601.DD_MMM_YYYY}"),
        header_pattern=regex(r"(Description of Transaction.*Transaction Amount)"),
        prev_balance_pattern=StatementBalancePatterns.UOB,
        transaction_pattern=DebitTransactionPatterns.UOB,
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=regex(rf"Period: .* to {ISO8601.DD_MMM_YYYY}"),
        header_pattern=regex(r"(Date.*Description.*Withdrawals.*Deposits.*Balance)"),
        transaction_pattern=DebitTransactionPatterns.UOB,
        transaction_bound=170,
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    identifiers = [
        [
            MetadataIdentifier(
                format="PDF 1.5",
                creator="Vault Rendering Engine",
                producer="Rendering Engine",
            ),
        ],
        [TextIdentifier("card.centre@uobgroup.com")],
    ]
    statement_configs = [credit, debit]
