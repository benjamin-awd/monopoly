from re import compile as regex

from monopoly.config import StatementConfig
from monopoly.constants import EntryType, InternalBankNames, SharedPatterns
from monopoly.identifiers import TextIdentifier

from .base import BankBase


class ExampleBank(BankBase):
    """Dummy class to help with reading the example PDF statement"""

    credit_config = StatementConfig(
        statement_type=EntryType.CREDIT,
        bank_name=InternalBankNames.EXAMPLE,
        statement_date_pattern=regex(r"(\d{2}\-\d{2}\-\d{4})"),
        header_pattern=regex(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        prev_balance_pattern=regex(
            r"(?P<description>LAST MONTH'S BALANCE?)\s+"
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=regex(
            r"(?P<transaction_date>\d+/\d+)\s*"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED
        ),
    )

    identifiers = [
        [
            TextIdentifier(text="HCBS12345(12345)"),
        ]
    ]

    statement_configs = [credit_config]
