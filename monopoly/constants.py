import os
from enum import Enum

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AccountType(Enum):
    CREDIT = "credit"


class BankNames(Enum):
    CITIBANK = "citibank"
    HSBC = "hsbc"
    OCBC = "ocbc"
    EXAMPLE = "monopoly"


class StatementFields(str, Enum):
    DATE = "date"
    DESCRIPTION = "description"
    AMOUNT = "amount"


class EmailSubjectRegex(str, Enum):
    OCBC = r"OCBC Bank: Your Credit Card e-Statement"
    HSBC = r"Your.HSBC.*eStatement"


class TransactionPatterns(str, Enum):
    OCBC = r"^(?P<date>\d+/\d+)\s*(?P<description>.*?)\s*(?P<amount>[\d.,]+)$"
    CITIBANK = (
        r"^(?P<date>\b\d{2}\s\w{3}\b)\s*"
        r"(?P<description>.*?)\s*"
        r"(?P<amount>[\d.,]+)$"
    )
    HSBC = (
        r"^\d{2}\s\w{3}\s*"
        r"(?P<date>\d{2}\s\w{3})\s.*?"
        r"(?P<description>\w.*?)\s*"
        r"(?P<amount>[\d.,]+)$"
    )
