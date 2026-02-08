import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier


class BankOfAmerica(BankBase):
    name = "bank_of_america"

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"for .* to {ISO8601.MMMM_DD_YYYY}"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(Date\s+Description\s+Amount)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.MM_DD_YY})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?P<polarity>\-)?"
            + SharedPatterns.AMOUNT
        ),
        transaction_date_format="%m/%d/%y",
        multiline_config=MultilineConfig(multiline_descriptions=True),
        safety_check=False,
    )

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"Statement Closing Date\s+{ISO8601.MM_DD_YYYY}"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(Date\s+Date\s+Description\s+Number\s+Number\s+Amount\s+Total)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
            rf"(?P<posting_date>{ISO8601.MM_DD})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?P<reference_number>\d{4})?\s+"
            + r"(?P<account_number>\d{4})?\s+"
            + r"(?P<polarity>\-)?"
            + SharedPatterns.AMOUNT
        ),
        transaction_date_format="%m/%d",
        multiline_config=MultilineConfig(multiline_descriptions=True),
        safety_check=False,
    )

    identifiers = [
        [
            MetadataIdentifier(
                format="PDF 1.5",
                creator="Bank of America",
                producer="TargetStream StreamEDS",
            )
        ]
    ]

    statement_configs = [debit, credit]
