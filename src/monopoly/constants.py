import re
from dataclasses import asdict
from enum import auto

from pydantic.dataclasses import dataclass
from strenum import StrEnum


# flake8: noqa
# pylint: disable=line-too-long
class DateFormats(StrEnum):
    D = r"(?:1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    DD = r"(?:01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    M = r"(?:1|2|3|4|5|6|7|8|9|10|11|12)"
    MM = r"(?:01|02|03|04|05|06|07|08|09|10|11|12)"
    MMM = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    MMMM = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    YY = r"(?:[2-5][0-9]\b)"
    YYYY = r"(?:20\d{2}\b)"


@dataclass
class DateRegexPatterns:
    """Holds date regex patterns used by the generic statement handler"""

    dd_mm: str = rf"\b({DateFormats.DD}[\/\-\s]{DateFormats.MM})"
    dd_mm_yy: str = (
        rf"\b({DateFormats.DD}[\/\-\s]{DateFormats.MM}[\/\-\s]{DateFormats.YY})"
    )
    dd_mmm: str = rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM})"
    dd_mmm_yy: str = rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM}[-\s]{DateFormats.YY})"
    dd_mmm_yyyy: str = (
        rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM}[,\s]{{1,2}}{DateFormats.YYYY})"
    )
    dd_mm_yyyy: str = (
        rf"\b({DateFormats.DD}[\/\-\s]{DateFormats.MM}[\/\-\s]{DateFormats.YYYY})"
    )
    mmmm_dd_yyyy: str = (
        rf"\b({DateFormats.MMMM}\s{DateFormats.DD}[,\s]{{1,2}}{DateFormats.YYYY})"
    )
    mmm_dd: str = rf"\b({DateFormats.MMM}[-\s]{DateFormats.DD})"
    mmm_dd_yyyy: str = (
        rf"\b({DateFormats.MMM}[-\s]{DateFormats.DD}[,\s]{{1,2}}{DateFormats.YYYY})"
    )

    def as_pattern_dict(self):
        return {k: re.compile(v, re.IGNORECASE) for k, v in asdict(self).items()}


# pylint: disable=unused-argument,no-self-argument
class AutoEnum(StrEnum):
    """Generates lower case values for enums
    e.g. CITIBANK -> citibank
    """

    def _generate_next_value_(name: str, *_):  # type: ignore
        return name.lower()


class EntryType(AutoEnum):
    CREDIT = auto()
    DEBIT = auto()


class BankNames(AutoEnum):
    CITIBANK = auto()
    DBS = auto()
    HSBC = auto()
    MAYBANK = auto()
    OCBC = auto()
    STANDARD_CHARTERED = auto()


class InternalBankNames(AutoEnum):
    EXAMPLE = auto()
    GENERIC = auto()


class Columns(AutoEnum):
    AMOUNT = auto()
    DATE = auto()
    DESCRIPTION = auto()
    SUFFIX = auto()
    TRANSACTION_DATE = auto()


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


class StatementBalancePatterns(StrEnum):
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
        r"(?P<description>PREVIOUS STATEMENT BALANCE?)\s+"
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


class CreditTransactionPatterns(StrEnum):
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


class DebitTransactionPatterns(StrEnum):
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


@dataclass
class Identifier:
    pass


@dataclass
class EncryptionIdentifier(Identifier):
    pdf_version: float
    algorithm: int
    revision: int
    length: int
    permissions: int


@dataclass
class MetadataIdentifier(Identifier):
    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    producer: str = ""
