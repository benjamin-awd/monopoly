import os
from enum import Enum

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AccountType(Enum):
    CREDIT = "credit"


class BankNames(Enum):
    CITIBANK = "citibank"
    HSBC = "hsbc"
    OCBC = "ocbc"


class BankStatement(str, Enum):
    DATE = "date"
    DESCRIPTION = "description"
    AMOUNT = "amount"


class EmailSubjectRegex(str, Enum):
    OCBC = r"OCBC Bank: Your Credit Card e-Statement"
    HSBC = r"Your.HSBC.*eStatement"
