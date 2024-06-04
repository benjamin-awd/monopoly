import re
from dataclasses import asdict
from enum import StrEnum, auto
from typing import Generic, TypeVar

from pydantic.dataclasses import dataclass


# flake8: noqa
# pylint: disable=line-too-long
class DateFormats(StrEnum):
    D = "(?:1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    DD = "(?:01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)"
    M = "(?:1|2|3|4|5|6|7|8|9|10|11|12)"
    MM = "(?:01|02|03|04|05|06|07|08|09|10|11|12)"
    MMM = "(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    MMMM = "(?:January|February|March|April|May|June|July|August|September|October|November|December)"


@dataclass
class DateRegexPatterns:
    """Holds date regex patterns used by the generic statement handler"""

    DD_MM: str = rf"\b({DateFormats.DD}[\/\-]{DateFormats.MM})"
    DD_MMM: str = rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM})"
    DD_MMM_YYYY: str = (
        rf"\b({DateFormats.DD}[-\s]{DateFormats.MMM}[,\s]{{1,2}}20\d{{2}})"
    )
    DD_MM_YYYY: str = rf"\b({DateFormats.DD}[\/\-]{DateFormats.MM}[\/\-]20\d{{2}})"
    MMMM_DD_YYYY: str = (
        rf"\b({DateFormats.MMMM}\s{DateFormats.DD}[,\s]{{1,2}}20\d{{2}})"
    )
    MMM_DD: str = rf"\b({DateFormats.MMM}[-\s]{DateFormats.DD})"
    MMM_DD_YYYY: str = (
        rf"\b({DateFormats.MMM}[-\s]{DateFormats.DD}[,\s]{{1,2}}20\d{{2}})"
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
    DEBIT_CREDIT_SUFFIX = r"(?P<suffix>CR\b|DR\b)?"
    AMOUNT = rf"(?P<amount>{COMMA_FORMAT}|\({COMMA_FORMAT}\s{{0,1}}\))\s*"
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
        rf"(?P<transaction_date>{DateRegexPatterns.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    CITIBANK = (
        rf"(?P<transaction_date>{DateRegexPatterns.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    HSBC = (
        rf"(?P<posting_date>{DateRegexPatterns.DD_MMM})\s+"
        rf"(?P<transaction_date>{DateRegexPatterns.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    OCBC = (
        r"(?P<transaction_date>\d+/\d+)\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    STANDARD_CHARTERED = (
        rf"(?P<transaction_date>{DateRegexPatterns.DD_MMM})\s+"
        rf"(?P<posting_date>{DateRegexPatterns.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?:(?P<transaction_ref>Transaction\sRef\s\d+)?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED
    )


class DebitTransactionPatterns(StrEnum):
    DBS = (
        rf"(?P<transaction_date>{DateRegexPatterns.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        + SharedPatterns.BALANCE
    )
    OCBC = (
        rf"(?P<transaction_date>{DateRegexPatterns.DD_MMM})\s+"
        rf"(?P<posting_date>{DateRegexPatterns.DD_MMM})\s+"
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
