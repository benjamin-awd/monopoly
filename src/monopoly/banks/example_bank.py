import re

from monopoly.config import StatementConfig
from monopoly.constants import EntryType, InternalBankNames, SharedPatterns
from monopoly.identifiers import TextIdentifier

from .base import BankBase


class ExampleBank(BankBase):
    """Dummy class to help with reading the example PDF statement."""

    name = InternalBankNames.EXAMPLE

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(r"(\d{2}\-\d{2}\-\d{4})"),
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        prev_balance_pattern=re.compile(
            r"(?P<description>LAST MONTH'S BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=re.compile(
            r"(?P<transaction_date>\d+/\d+)\s*" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
        ),
        transaction_date_format="%d/%m",
    )

    identifiers = [
        [
            TextIdentifier(text="HCBS12345(12345)"),
        ]
    ]

    statement_configs = [credit]
