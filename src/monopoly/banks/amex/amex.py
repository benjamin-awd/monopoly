import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, PaymentSummaryConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601, DateFormats
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

# MM/DD/YY reaching back to 2010: US statements are kept online for years, and the shared
# two-digit year starts at 2020
US_MM_DD_YY = rf"\b({DateFormats.MM}/{DateFormats.DD}/[1-5][0-9]\b)"


class Amex(BankBase):
    name = "amex"

    platinum = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"From .* to {ISO8601.DD_MM_YYYY}"),
        # "Statement Period   From 21.12.2024 to 20.01.2025": start is the "From" date
        period_start_pattern=re.compile(r"From (\d{2}\.\d{2}\.\d{4}) to"),
        transaction_date_format="%d.%m.%y",
        header_pattern=re.compile(r"(Details.*Foreign Spending.*Amount)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MM_YY})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED
        ),
        multiline_config=MultilineConfig(multiline_direction=True),
    )

    # Cards issued in the United States: USD, US dates, and an "Account Ending 4-12345" line
    # in every page header
    us = StatementConfig(
        currency="USD",
        statement_type=EntryType.CREDIT,
        # "Closing Date 09/07/26", which may share a line with "Next Closing Date 10/07/26"
        statement_date_pattern=re.compile(rf"(?<!Next )Closing Date\s+{US_MM_DD_YY}"),
        account_pattern=re.compile(r"Account Ending\s+(?P<account>\d-\d{5})\b"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(Account Ending\s+\d-\d{5})"),
        # "Previous Balance   $1,234.56", or "CR$12.34" when it was a credit balance. Counted
        # with the rows, they add up to the New Balance, which the statement always prints: the
        # charges alone don't appear once there are fees or interest.
        prev_balance_pattern=re.compile(
            r"(?P<description>Previous Balance)\s+(?P<direction>CR)?\$(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"
        ),
        # "08/16/26   HOTEL NAME   WASHINGTON   DC   $984.32"; credits are "-$253.41", and a
        # "*" after the date marks it as the posting date
        transaction_pattern=re.compile(
            rf"^\s*(?P<transaction_date>{US_MM_DD_YY})\*?\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?P<direction>-)?\$(?P<amount>"
            + SharedPatterns.COMMA_FORMAT
            + r")$"
        ),
        transaction_date_format="%m/%d/%y",
        payment_summary_config=PaymentSummaryConfig(
            payment_due_date=re.compile(rf"Payment Due Date\s+(?P<due_date>{US_MM_DD_YY})"),
            total_amount_due=re.compile(
                r"^\s*New Balance\s+(?P<direction>-)?\$(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"
            ),
            minimum_payment=re.compile(r"^\s*Minimum Payment Due\s+\$(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"),
        ),
    )

    identifiers = [
        [
            TextIdentifier("The Platinum Credit Card"),
            TextIdentifier("americanexpress.com"),
        ],
        [
            # US statements are titled "CSF.CRS.US.MTH...." by the issuer's statement system
            MetadataIdentifier(title="CSF.CRS.US.", creator="FIS Global Corp."),
            TextIdentifier("americanexpress.com"),
        ],
        [
            # US statements issued before 2024, as the online archive renders them
            MetadataIdentifier(title="PRO Document", creator="PRO HLCAPI"),
            TextIdentifier("americanexpress.com"),
            TextIdentifier("Account Ending"),
        ],
    ]

    statement_configs = [platinum, us]
