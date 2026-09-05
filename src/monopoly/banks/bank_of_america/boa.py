import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier


class BankOfAmerica(BankBase):
    name = "bank_of_america"

    debit = StatementConfig(
        currency="USD",
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"for .* to {ISO8601.MMMM_DD_YYYY}"),
        # period end is the "to" date above; period start is the preceding date
        period_start_pattern=re.compile(rf"for {ISO8601.MMMM_DD_YYYY} to"),
        # masked account number, e.g. "Account number: 5108 2276 3391"
        account_pattern=re.compile(r"(?i)Account number:\s+(?P<account>[\dX]{4}(?:[ -][\dX]{2,4})+)"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(Date\s+Description\s+Amount)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.MM_DD_YY})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?P<direction>\-)?"
            + SharedPatterns.AMOUNT
        ),
        transaction_date_format="%m/%d/%y",
        multiline_config=MultilineConfig(multiline_descriptions=True),
        safety_check=False,
    )

    credit = StatementConfig(
        currency="USD",
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"Statement Closing Date\s+{ISO8601.MM_DD_YYYY}"),
        # masked account number, e.g. "Account Number  4417 88XX XXXX 2031"
        account_pattern=re.compile(r"(?i)Account Number\s+(?P<account>[\dX]{4}(?:[ -][\dX]{2,4})+)"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(Date\s+Date\s+Description\s+Number\s+Number\s+Amount\s+Total)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
            rf"(?P<posting_date>{ISO8601.MM_DD})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?P<reference_number>\d{4})?\s+"
            + r"(?P<account_number>\d{4})?\s+"
            + r"(?P<direction>\-)?"
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
