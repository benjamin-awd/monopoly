from enum import StrEnum, auto

from pydantic.dataclasses import dataclass


# pylint: disable=unused-argument,no-self-argument
class AutoEnum(StrEnum):
    """Generates lower case values for enums
    e.g. CITIBANK -> citibank
    """

    def _generate_next_value_(name: str, *_):  # type: ignore
        return name.lower()


class AccountType(AutoEnum):
    CREDIT = auto()


class BankNames(AutoEnum):
    CITIBANK = auto()
    DBS = auto()
    HSBC = auto()
    OCBC = auto()
    STANDARD_CHARTERED = auto()
    EXAMPLE = auto()


class StatementFields(AutoEnum):
    TRANSACTION_DATE = auto()
    DESCRIPTION = auto()
    AMOUNT = auto()


class SharedPatterns(StrEnum):
    """
    AMOUNT matches the following patterns:
    1,123.12 | 123.12 | (123.12) | ( 123.12) | 123.12 CR
    """

    AMOUNT = r"(?P<amount>[\d.,]+|\([\d.,\s]+\)$)\s*(?P<suffix>CR|DR)?$"
    AMOUNT_WITH_CASHBACK = r"(?P<amount>[\d.,]+|\([\d.,\s]+\))$"
    DESCRIPTION = r"(?P<description>.*?)\s+"
    TRANSACTION_DATE_ABBREVIATED_ALL_CAPS = r"(?P<transaction_date>\d{2}\s[A-Z]{3})\s+"
    TRANSACTION_DATE_ABBREVIATED_PROPER_CASE = (
        r"(?P<transaction_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
    )
    POSTING_DATE_ABBREVIATED_PROPER = r"(?P<posting_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"


class StatementBalancePatterns(StrEnum):
    DBS = r"(?P<description>PREVIOUS BALANCE?)\s+" + SharedPatterns.AMOUNT
    CITIBANK = (
        r"(?P<description>BALANCE PREVIOUS STATEMENT?)\s+" + SharedPatterns.AMOUNT
    )
    HSBC = r"(?P<description>Previous Statement Balance?)\s+" + SharedPatterns.AMOUNT
    OCBC = r"(?P<description>LAST MONTH'S BALANCE?)\s+" + SharedPatterns.AMOUNT
    STANDARD_CHARTERED = (
        r"(?P<description>BALANCE FROM PREVIOUS STATEMENT?)\s+" + SharedPatterns.AMOUNT
    )


class TransactionPatterns(StrEnum):
    DBS = (
        SharedPatterns.TRANSACTION_DATE_ABBREVIATED_ALL_CAPS
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT
    )
    CITIBANK = (
        SharedPatterns.TRANSACTION_DATE_ABBREVIATED_ALL_CAPS
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_WITH_CASHBACK
    )
    HSBC = (
        SharedPatterns.POSTING_DATE_ABBREVIATED_PROPER
        + SharedPatterns.TRANSACTION_DATE_ABBREVIATED_PROPER_CASE
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT
    )
    OCBC = (
        r"^(?P<transaction_date>\d+/\d+)\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_WITH_CASHBACK
    )
    STANDARD_CHARTERED = (
        SharedPatterns.POSTING_DATE_ABBREVIATED_PROPER
        + SharedPatterns.TRANSACTION_DATE_ABBREVIATED_PROPER_CASE
        + SharedPatterns.DESCRIPTION
        + r"(?:(?P<transaction_ref>Transaction\sRef\s\d+)?)\s+"
        + SharedPatterns.AMOUNT
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
