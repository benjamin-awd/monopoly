"""Store statement-related enums and constants."""

from enum import auto

from strenum import StrEnum

from monopoly.enums import AutoEnum


class EntryType(AutoEnum):
    CREDIT = auto()
    DEBIT = auto()


class Columns(AutoEnum):
    AMOUNT = auto()
    BALANCE = auto()
    DATE = auto()
    DESCRIPTION = auto()
    POLARITY = auto()
    TRANSACTION_DATE = auto()


class SharedPatterns(StrEnum):
    """
    Attempt to keep patterns DRY.

    AMOUNT matches the following patterns:
    1,123.12 | 123.12 | (123.12) | ( 123.12) | 123.12 CR | -1,123.12.

    AMOUNT_EXTENDED is generally used for credit statements and to
    find statement balances, while AMOUNT_EXTENDED_WITHOUT_EOL is used
    for debit statements, since debit statements have the amount + balances
    on a single line, and we only want the amount.
    """

    COMMA_FORMAT = r"\d{1,3}(,\d{3})*\.\d*"
    ENCLOSED_COMMA_FORMAT = rf"\({COMMA_FORMAT}\s{{0,1}}\))"
    OPTIONAL_NEGATIVE_SYMBOL = r"(?:-)?"
    POLARITY = r"(?P<polarity>CR\b|DR\b|DB\b|\+|\-)?\s*"

    AMOUNT = rf"(?P<amount>{COMMA_FORMAT}|{ENCLOSED_COMMA_FORMAT}\s*"
    AMOUNT_EXTENDED_WITHOUT_EOL = AMOUNT + POLARITY
    AMOUNT_EXTENDED = AMOUNT_EXTENDED_WITHOUT_EOL + r"$"

    BALANCE = rf"(?P<balance>{COMMA_FORMAT})?$"
    DESCRIPTION = r"(?P<description>.*?)\s+"
    TRANSACTION_DATE_ABBREVIATED_ALL_CAPS = r"(?P<transaction_date>\d{2}\s[A-Z]{3})\s+"
    TRANSACTION_DATE_ABBREVIATED_PROPER_CASE = r"(?P<transaction_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
    POSTING_DATE_ABBREVIATED_PROPER = r"(?P<posting_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
