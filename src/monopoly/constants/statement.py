"""This file stores statement-related enums and constants"""

from strenum import StrEnum

from .date import DateRegexPatterns
from .enums import RegexEnum


class SharedPatterns(StrEnum):
    """
    AMOUNT matches the following patterns:
    1,123.12 | 123.12 | (123.12) | ( 123.12) | 123.12 CR

    AMOUNT_EXTENDED is generally used for credit statements and to
    find statement balances, while AMOUNT_EXTENDED_WITHOUT_EOL is used
    for debit statements, since debit statements have the amount + balances
    on a single line, and we only want the amount.
    """

    COMMA_FORMAT = r"\d{1,3}(,\d{3})*\.\d*"
    ENCLOSED_COMMA_FORMAT = rf"\({COMMA_FORMAT}\s{{0,1}}\))"
    DEBIT_CREDIT_SUFFIX = r"(?P<suffix>CR\b|DR\b|\+|\-)?\s*"

    AMOUNT = rf"(?P<amount>{COMMA_FORMAT}|{ENCLOSED_COMMA_FORMAT}\s*"
    AMOUNT_EXTENDED_WITHOUT_EOL = AMOUNT + DEBIT_CREDIT_SUFFIX
    AMOUNT_EXTENDED = AMOUNT_EXTENDED_WITHOUT_EOL + r"$"

    BALANCE = rf"(?P<balance>{COMMA_FORMAT})?$"
    DESCRIPTION = r"(?P<description>.*?)\s+"
    TRANSACTION_DATE_ABBREVIATED_ALL_CAPS = r"(?P<transaction_date>\d{2}\s[A-Z]{3})\s+"
    TRANSACTION_DATE_ABBREVIATED_PROPER_CASE = (
        r"(?P<transaction_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
    )
    POSTING_DATE_ABBREVIATED_PROPER = r"(?P<posting_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"


class StatementBalancePatterns(RegexEnum):
    DBS = (
        r"(?P<description>PREVIOUS BALANCE?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    CITIBANK = (
        r"(?P<description>BALANCE PREVIOUS STATEMENT?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    HSBC = (
        r"(?P<description>Previous Statement Balance?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    MAYBANK = (
        r"(?P<description>YOUR PREVIOUS STATEMENT BALANCE?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    OCBC = (
        r"(?P<description>LAST MONTH'S BALANCE?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    STANDARD_CHARTERED = (
        r"(?P<description>BALANCE FROM PREVIOUS STATEMENT?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )


class CreditTransactionPatterns(RegexEnum):
    DBS = (
        rf"(?P<transaction_date>{DateRegexPatterns.dd_mmm})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    CITIBANK = (
        rf"(?P<transaction_date>{DateRegexPatterns.dd_mmm})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    HSBC = (
        rf"(?P<posting_date>{DateRegexPatterns.dd_mmm})\s+"
        rf"(?P<transaction_date>{DateRegexPatterns.dd_mmm})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    MAYBANK = (
        rf"(?P<posting_date>{DateRegexPatterns.dd_mm})\s+"
        rf"(?P<transaction_date>{DateRegexPatterns.dd_mm})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    OCBC = (
        r"(?P<transaction_date>\d+/\d+)\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    STANDARD_CHARTERED = (
        rf"(?P<transaction_date>{DateRegexPatterns.dd_mmm})\s+"
        rf"(?P<posting_date>{DateRegexPatterns.dd_mmm})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?:(?P<transaction_ref>Transaction\sRef\s\d+)?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED
    )


class DebitTransactionPatterns(RegexEnum):
    DBS = (
        rf"(?P<transaction_date>{DateRegexPatterns.dd_mmm})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        + SharedPatterns.BALANCE
    )
    MAYBANK = (
        rf"(?P<transaction_date>{DateRegexPatterns.dd_mm_yy})\s+"
        + SharedPatterns.DESCRIPTION
        # remove *\s
        + SharedPatterns.AMOUNT[:-3]
        + r"(?P<suffix>\-|\+)\s+"
        + SharedPatterns.BALANCE
    )
    OCBC = (
        rf"(?P<transaction_date>{DateRegexPatterns.dd_mmm})\s+"
        rf"(?P<posting_date>{DateRegexPatterns.dd_mmm})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        + SharedPatterns.BALANCE
    )
