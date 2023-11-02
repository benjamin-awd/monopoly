import os
from enum import StrEnum, auto

from pydantic.dataclasses import dataclass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# pylint: disable=unused-argument,no-self-argument
class AutoEnum(StrEnum):
    """Generates lower case values for enums
    e.g. CITIBANK -> citibank
    """

    def _generate_next_value_(name: str, *args):  # type: ignore
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
    AMOUNT = r"(?P<amount>[\d.,]+)$"
    DESCRIPTION = r"(?P<description>.*?)\s+"
    TRANSACTION_DATE_ABBREVIATED_ALL_CAPS = r"(?P<transaction_date>\d{2}\s[A-Z]{3})\s+"
    TRANSACTION_DATE_ABBREVIATED_PROPER_CASE = (
        r"(?P<transaction_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
    )
    POSTING_DATE_ABBREVIATED_PROPER = r"(?P<posting_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"


class TransactionPatterns(StrEnum):
    DBS = (
        SharedPatterns.TRANSACTION_DATE_ABBREVIATED_ALL_CAPS
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT
    )
    CITIBANK = (
        SharedPatterns.TRANSACTION_DATE_ABBREVIATED_ALL_CAPS
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT
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
        + SharedPatterns.AMOUNT
    )
    STANDARD_CHARTERED = (
        SharedPatterns.POSTING_DATE_ABBREVIATED_PROPER
        + SharedPatterns.TRANSACTION_DATE_ABBREVIATED_PROPER_CASE
        + SharedPatterns.DESCRIPTION
        + r"(?P<transaction_ref>Transaction\sRef\s\d+)\s+"
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
