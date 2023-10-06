import os
from enum import Enum

from monopoly.helpers.enums import BankStatement, EmailSubjectRegex

DATE = BankStatement.DATE.value
DESCRIPTION = BankStatement.DESCRIPTION.value
AMOUNT = BankStatement.AMOUNT.value
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCBC = EmailSubjectRegex.OCBC.value
HSBC = EmailSubjectRegex.HSBC.value


class AccountType(Enum):
    CREDIT = "credit"


class BankNames(Enum):
    CITIBANK = "citibank"
    HSBC = "hsbc"
    OCBC = "ocbc"
