import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601, DateFormats
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Schwab(BankBase):
    name = "schwab_bank"

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        # Matches two statement date formats:
        #   Single-line range: "January 1-30, 2026"
        #   Two-line period:   "January 31, 2026 to" / "February 27, 2026"
        # In both cases, the end date is captured.
        statement_date_pattern=re.compile(
            rf"(?P<month>{DateFormats.MMMM})"
            r"\s+\d{1,2}[-,](?:\s+.+\s+"
            rf"(?:{DateFormats.MMMM})\s+)?"
            r"(?P<day>\d{1,2}),?\s+"
            r"(?P<year>\d{4})"
        ),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(
            r"(Posted Description\s+Debits\s+Credits\s+Balance)"
        ),
        transaction_date_format="%m/%d",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
            + SharedPatterns.DESCRIPTION
            + r"\$(?P<amount>"
            + SharedPatterns.COMMA_FORMAT
            + r")\s+"
            + r"\$(?P<balance>"
            + SharedPatterns.COMMA_FORMAT
            + r")"
        ),
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            multiline_statement_date=True,
        ),
        safety_check=False,
    )

    identifiers = [
        [
            MetadataIdentifier(author="Charles Schwab & Co. Inc."),
            TextIdentifier("Schwab Bank"),
        ]
    ]

    statement_configs = [debit]
