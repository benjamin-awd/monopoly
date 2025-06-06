"""Store statement-related enums and constants."""

from enum import auto

from strenum import StrEnum

from monopoly.enums import AutoEnum, RegexEnum

from .date import ISO8601


class EntryType(AutoEnum):
    CREDIT = auto()
    DEBIT = auto()


class BankNames(AutoEnum):
    AMEX = auto()
    BANK_OF_AMERICA = auto()
    CHASE = auto()
    CITIBANK = auto()
    DBS = auto()
    HSBC = auto()
    MAYBANK = auto()
    OCBC = auto()
    STANDARD_CHARTERED = auto()
    UOB = auto()
    ZKB = auto()
    TRUST = auto()


class InternalBankNames(AutoEnum):
    EXAMPLE = auto()
    GENERIC = auto()


class Columns(AutoEnum):
    AMOUNT = auto()
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
    POLARITY = r"(?P<polarity>CR\b|DR\b|\+|\-)?\s*"

    AMOUNT = rf"(?P<amount>{COMMA_FORMAT}|{ENCLOSED_COMMA_FORMAT}\s*"
    AMOUNT_EXTENDED_WITHOUT_EOL = AMOUNT + POLARITY
    AMOUNT_EXTENDED = AMOUNT_EXTENDED_WITHOUT_EOL + r"$"

    BALANCE = rf"(?P<balance>{COMMA_FORMAT})?$"
    DESCRIPTION = r"(?P<description>.*?)\s+"
    TRANSACTION_DATE_ABBREVIATED_ALL_CAPS = r"(?P<transaction_date>\d{2}\s[A-Z]{3})\s+"
    TRANSACTION_DATE_ABBREVIATED_PROPER_CASE = r"(?P<transaction_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
    POSTING_DATE_ABBREVIATED_PROPER = r"(?P<posting_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"


class StatementBalancePatterns(RegexEnum):
    DBS = r"(?P<description>PREVIOUS BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    CITIBANK = r"(?P<description>BALANCE PREVIOUS STATEMENT?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    HSBC = r"(?P<description>Previous Statement Balance?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    MAYBANK = r"(?P<description>YOUR PREVIOUS STATEMENT BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    OCBC = r"(?P<description>LAST MONTH'S BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    STANDARD_CHARTERED = (
        r"(?P<description>BALANCE FROM PREVIOUS STATEMENT?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    UOB = r"(?P<description>PREVIOUS BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    TRUST = r"(?P<description>Previous balance?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL


class CreditTransactionPatterns(RegexEnum):
    AMEX_PLATINUM = (
        rf"(?P<transaction_date>{ISO8601.DD_MM_YY})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    )
    BANK_OF_AMERICA = (
        rf"(?P<transaction_date>{ISO8601.MM_DD_YY})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?P<polarity>\-)?"
        + SharedPatterns.AMOUNT
    )
    DBS = rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    CHASE = rf"(?P<transaction_date>{ISO8601.MM_DD})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    CITIBANK = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    )
    HSBC = (
        rf"(?P<posting_date>{ISO8601.DD_MMM_RELAXED})\s+"
        rf"(?P<transaction_date>{ISO8601.DD_MMM_RELAXED})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    MAYBANK = (
        rf"(?P<posting_date>{ISO8601.DD_MM})\s+"
        rf"(?P<transaction_date>{ISO8601.DD_MM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    )
    OCBC = r"(?P<transaction_date>\d+/\d+)\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    STANDARD_CHARTERED = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?:(?P<transaction_ref>Transaction\sRef\s\d+)?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED
    )
    UOB = (
        rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    )
    TRUST = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        r"(?P<description>(?:(?!Total outstanding balance).)*?)"
        r"(?P<polarity>\+)?"
        f"{SharedPatterns.AMOUNT}"
        r"$"  # necessary to ignore FCY
    )


class DebitTransactionPatterns(RegexEnum):
    DBS = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    DBS_POSB_CONSOLIDATED = (
        rf"(?P<transaction_date>{ISO8601.DD_MM_YYYY})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    MAYBANK = (
        rf"(?P<transaction_date>{ISO8601.DD_MM_YY})\s+"
        + SharedPatterns.DESCRIPTION
        # remove *\s
        + SharedPatterns.AMOUNT[:-3]
        + r"(?P<polarity>\-|\+)\s+"
        + SharedPatterns.BALANCE
    )
    OCBC = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        + SharedPatterns.BALANCE
    )
    UOB = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        + SharedPatterns.BALANCE
    )
    ZKB = (
        rf"(?P<transaction_date>{ISO8601.DD_MM_YYYY})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?P<amount>\d{1,3}(\'\d{3})*(\.\d+)?)\s+"
        + rf"(?P<value_date>{ISO8601.DD_MM_YYYY})\s+"
        + r"(?P<balance>\d{1,3}(\'\d{3})*(\.\d+)?)$"
    )
