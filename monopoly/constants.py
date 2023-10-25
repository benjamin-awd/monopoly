import os
from enum import Enum

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AccountType(Enum):
    CREDIT = "credit"


class BankNames(Enum):
    CITIBANK = "citibank"
    HSBC = "hsbc"
    OCBC = "ocbc"
    STANDARD_CHARTERED = "standard_chartered"


class StatementFields(str, Enum):
    TRANSACTION_DATE = "transaction_date"
    DESCRIPTION = "description"
    AMOUNT = "amount"


class EmailSubjectRegex(str, Enum):
    OCBC = r"OCBC Bank: Your Credit Card e-Statement"
    HSBC = r"Your.HSBC.*eStatement"


class TransactionPatterns(str, Enum):
    OCBC = (
        r"(?P<transaction_date>\d+/\d+)\s+(?P<description>.*?)\s+(?P<amount>[\d.,]+)$"
    )
    CITIBANK = (
        r"(?P<transaction_date>\b\d{2}\s\w{3}\b)\s+"
        r"(?P<description>.*?)\s+"
        r"(?P<amount>[\d.,]+)$"
    )
    HSBC = (
        r"(?P<posting_date>\d{2}\s\w{3})\s+"
        r"(?P<transaction_date>\d{2}\s\w{3})\s.*?"
        r"(?P<description>\w.*?)\s+"
        r"(?P<amount>[\d.,]+)$"
    )
    STANDARD_CHARTERED = (
        r"(?P<posting_date>\d{2}\s\w{3})\s+"
        r"(?P<transaction_date>\d{2}\s\w{3})\s+"
        r"(?P<description>\w.*)\s+"
        r"(?P<transaction_ref>Transaction Ref[\d\s]+)\s+"
        r"(?P<amount>[\d.,]+)$"
    )
