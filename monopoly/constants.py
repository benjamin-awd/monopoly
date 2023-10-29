import os
from enum import StrEnum, auto

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


class EmailSubjectRegex(StrEnum):
    OCBC = r"OCBC Bank: Your Credit Card e-Statement"
    HSBC = r"Your.HSBC.*eStatement"


class SharedPatterns(StrEnum):
    AMOUNT = r"(?P<amount>[\d.,]+)$"
    DESCRIPTION = r"(?P<description>.*?)\s+"


class TransactionPatterns(StrEnum):
    DBS = (
        r"^(?P<transaction_date>\d{2}\s[A-Z]{3})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT
    )
    CITIBANK = (
        r"^(?P<transaction_date>\b\d{2}\s\w{3}\b)\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT
    )
    HSBC = (
        r"^(?P<posting_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
        r"(?P<transaction_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT
    )
    OCBC = (
        r"^(?P<transaction_date>\d+/\d+)\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT
    )
    STANDARD_CHARTERED = (
        r"^(?P<posting_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
        r"(?P<transaction_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?P<transaction_ref>Transaction\sRef\s\d+)\s+"
        + SharedPatterns.AMOUNT
    )
