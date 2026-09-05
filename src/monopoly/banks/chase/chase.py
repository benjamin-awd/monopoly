import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Chase(BankBase):
    name = "chase"

    credit = StatementConfig(
        currency="USD",
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(r"Statement Date:\s+(.*)"),
        # "Opening/Closing Date  12/18/18 - 01/17/19": opening date is the period start
        period_start_pattern=re.compile(r"Opening/Closing Date\s+(\d{2}/\d{2}/\d{2})\s*-"),
        # "Account Number: 1234 5678 9012 2037" in the account summary block
        account_pattern=re.compile(r"(?i)Account Number:\s+(?P<account>\d{4} \d{4} \d{4} \d{4})"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(.*Transaction.*Merchant Name .*\$ Amount)"),
        transaction_date_format="%m/%d",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?P<direction>\-)?"
            + r"(?P<amount>(\d{1,3}(,\d{3})*|\d*)\.\d+)$"
        ),
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    identifiers = [
        [
            MetadataIdentifier(
                format="PDF 1.7",
                producer="OpenText Output Transformation Engine - 23.4",
            ),
            TextIdentifier("Chase"),
        ]
    ]

    statement_configs = [credit]
