from enum import Enum


class BankStatement(str, Enum):
    DATE = "date"
    DESCRIPTION = "description"
    AMOUNT = "amount"


class Prefix(str, Enum):
    OCBC_365 = "OCBC 365 CREDIT CARD"
