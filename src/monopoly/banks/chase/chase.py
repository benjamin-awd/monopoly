import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, PaymentSummaryConfig, StatementConfig
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
        # "Account Number: 1234 5678 9012 2037" in the account summary block; recent statements
        # mask all but the last 4: "Account Number: XXXX XXXX XXXX 2037"
        account_pattern=re.compile(r"(?i)Account Number:\s+(?P<account>[\dX]{4}(?: [\dX]{4}){3})"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(.*Transaction.*Merchant Name .*\$ Amount)"),
        # "Previous Balance   $1,234.56" in the account summary, "-$12.34" when it was a credit.
        # Counted with the rows, they add up to the New Balance, which every statement prints:
        # the purchases alone aren't a printed figure once there are fees or interest.
        prev_balance_pattern=re.compile(
            r"(?P<description>Previous Balance)\s+(?P<direction>-)?\$(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"
        ),
        transaction_date_format="%m/%d",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?P<direction>\-)?"
            + r"(?P<amount>(\d{1,3}(,\d{3})*|\d*)\.\d+)$"
        ),
        multiline_config=MultilineConfig(multiline_descriptions=True),
        payment_summary_config=PaymentSummaryConfig(
            # the payment coupon prints each label with a colon, its value on the same line
            payment_due_date=re.compile(r"Payment Due Date:\s+(?P<due_date>\d{2}/\d{2}/\d{2})"),
            total_amount_due=re.compile(
                r"New Balance:\s+(?P<direction>-)?\$(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"
            ),
            minimum_payment=re.compile(r"Minimum Payment Due:\s+\$(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"),
        ),
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
