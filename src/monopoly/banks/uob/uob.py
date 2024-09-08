import logging
from re import compile as regex

from monopoly.config import StatementConfig
from monopoly.constants import (
    BankNames,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Uob(BankBase):
    credit_config = StatementConfig(
        statement_type=EntryType.CREDIT,
        bank_name=BankNames.UOB,
        statement_date_pattern=regex(rf"Statement Date.*{ISO8601.DD_MMM_YYYY}"),
        header_pattern=regex(r"(Description of Transaction.*Transaction Amount)"),
        prev_balance_pattern=StatementBalancePatterns.UOB,
        transaction_pattern=DebitTransactionPatterns.UOB,
        multiline_transactions=True,
    )

    debit_config = StatementConfig(
        statement_type=EntryType.DEBIT,
        bank_name=BankNames.UOB,
        statement_date_pattern=regex(rf"Period: .* to {ISO8601.DD_MMM_YYYY}"),
        header_pattern=regex(r"(Date.*Description.*Withdrawals.*Deposits.*Balance)"),
        transaction_pattern=DebitTransactionPatterns.UOB,
        transaction_bound=170,
        multiline_transactions=True,
    )

    identifiers = [
        [
            MetadataIdentifier(
                format="PDF 1.5",
                creator="Vault Rendering Engine",
                producer="Rendering Engine",
            ),
        ]
    ]
    statement_configs = [credit_config, debit_config]
