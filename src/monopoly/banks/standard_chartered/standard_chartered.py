import logging
from re import compile as regex

from monopoly.config import StatementConfig
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class StandardChartered(BankBase):
    credit_config = StatementConfig(
        statement_type=EntryType.CREDIT,
        bank_name=BankNames.STANDARD_CHARTERED,
        statement_date_pattern=regex(r"(\d{2}\s\w+\s\d{4})"),
        header_pattern=regex(r"(Transaction.*Posting.*Amount)"),
        prev_balance_pattern=StatementBalancePatterns.STANDARD_CHARTERED,
        transaction_pattern=CreditTransactionPatterns.STANDARD_CHARTERED,
    )

    identifiers = [
        [
            MetadataIdentifier(
                title="eStatement",
                producer="iText",
            ),
            TextIdentifier("Standard Chartered"),
        ]
    ]

    statement_configs = [credit_config]
