from enum import StrEnum, auto

from pydantic.dataclasses import dataclass


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
    EXAMPLE = auto()
    DBS = auto()
    HSBC = auto()
    OCBC = auto()
    STANDARD_CHARTERED = auto()


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

    DEBIT_CREDIT_SUFFIX = r"(?P<suffix>CR|DR)?"
    AMOUNT = r"(?P<amount>[\d.,]+|\([\d.,\s]+\))\s*"
    AMOUNT_EXTENDED_WITHOUT_EOL = AMOUNT + DEBIT_CREDIT_SUFFIX
    AMOUNT_EXTENDED = AMOUNT_EXTENDED_WITHOUT_EOL + r"$"
    BALANCE = r"(?:(?P<balance>[\d.,]+)\s*)?$"
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
        SharedPatterns.TRANSACTION_DATE_ABBREVIATED_ALL_CAPS
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    CITIBANK = (
        SharedPatterns.TRANSACTION_DATE_ABBREVIATED_ALL_CAPS
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    HSBC = (
        SharedPatterns.POSTING_DATE_ABBREVIATED_PROPER
        + SharedPatterns.TRANSACTION_DATE_ABBREVIATED_PROPER_CASE
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    OCBC = (
        r"(?P<transaction_date>\d+/\d+)\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    STANDARD_CHARTERED = (
        SharedPatterns.POSTING_DATE_ABBREVIATED_PROPER
        + SharedPatterns.TRANSACTION_DATE_ABBREVIATED_PROPER_CASE
        + SharedPatterns.DESCRIPTION
        + r"(?:(?P<transaction_ref>Transaction\sRef\s\d+)?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED
    )


class DebitTransactionPatterns(StrEnum):
    DBS = (
        SharedPatterns.TRANSACTION_DATE_ABBREVIATED_PROPER_CASE
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        + SharedPatterns.BALANCE
    )
    OCBC = (
        SharedPatterns.TRANSACTION_DATE_ABBREVIATED_ALL_CAPS
        + r"(?P<value_date>\d{2}\s[A-Z]{3})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        + SharedPatterns.BALANCE
    )


@dataclass
class EncryptionIdentifier:
    pdf_version: float
    algorithm: int
    revision: int
    length: int
    permissions: int


@dataclass
class MetadataIdentifier:
    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    producer: str = ""
