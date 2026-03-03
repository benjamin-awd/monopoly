import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class UsBank(BankBase):
    name = "usbank"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"Closing Date:\s+{ISO8601.MM_DD_YYYY}"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(
            r"(Date\s+Date\s+Ref #\s+Transaction Description\s+Amount)"
        ),
        transaction_date_format="%m/%d",
        transaction_pattern=re.compile(
            rf"(?P<posting_date>{ISO8601.MM_DD})\s+"
            rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
            r"\w+\s+"  # reference number
            + SharedPatterns.DESCRIPTION
            + r"\$"
            + SharedPatterns.AMOUNT_EXTENDED
        ),
    )

    identifiers = [
        [
            MetadataIdentifier(creator="AIM, F3"),
            TextIdentifier("U.S. Bank"),
        ]
    ]

    statement_configs = [credit]
