import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import DateFormats
from monopoly.identifiers import MetadataIdentifier


class CapitalOneUS(BankBase):
    """Capital One 360 bank statements (US): every 360 account in one PDF, each in its own section."""

    name = "capital_one_us"

    debit = StatementConfig(
        currency="USD",
        statement_type=EntryType.DEBIT,
        # "STATEMENT PERIOD   Aug 1 - Aug 31, 2026": the end date is the statement date
        statement_date_pattern=re.compile(
            rf"{DateFormats.MMM}\s+{DateFormats.D}\s+-\s+"
            rf"(?P<month>{DateFormats.MMM})\s+(?P<day>{DateFormats.D}),\s+(?P<year>{DateFormats.YYYY})"
        ),
        # the period is a calendar month, so the start shares the end date's year
        period_start_pattern=re.compile(
            rf"(?P<month>{DateFormats.MMM})\s+(?P<day>{DateFormats.D})\s+-\s+"
            rf"{DateFormats.MMM}\s+{DateFormats.D},\s+(?P<year>{DateFormats.YYYY})"
        ),
        # each account's section opens with "360 Checking - 12345671234"; the summary's
        # "360 Checking...1234" lines don't match
        account_pattern=re.compile(r"\b360 [A-Za-z ]+? - (?P<account>\d{6,})\b"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(DATE\s+DESCRIPTION\s+CATEGORY\s+AMOUNT\s+BALANCE)"),
        # "Aug 7   Check Deposit (Mobile)   Credit   + $143.66   $5,889.04"; the opening and
        # closing balance lines have no category or amount
        transaction_pattern=re.compile(
            rf"^\s*(?P<transaction_date>{DateFormats.MMM}\s+{DateFormats.D})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?:Credit|Debit)\s+"
            + r"(?P<direction>[+-])\s*\$(?P<amount>"
            + SharedPatterns.COMMA_FORMAT
            + r")\s+-?\$(?P<balance>"
            + SharedPatterns.COMMA_FORMAT
            + r")\s*$"
        ),
        # a long description wraps onto a second line and takes the amount with it:
        # "Jul 9   Withdrawal from ... TAX   Debit   $1,008.15" then "   PAYMENT   - $100.00"
        multiline_config=MultilineConfig(multiline_descriptions=True, multiline_amount=True),
        # no totals are printed, only each account's opening and closing balance
        safety_check=False,
    )

    identifiers = [[MetadataIdentifier(author="capitalone.com", title="Bank Statement")]]

    statement_configs = [debit]
