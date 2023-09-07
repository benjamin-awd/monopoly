from enum import Enum


class BankStatement(str, Enum):
    DATE = "date"
    DESCRIPTION = "description"
    AMOUNT = "amount"


class EmailSubjectRegex(str, Enum):
    OCBC = r"OCBC Bank: Your Credit Card e-Statement"
    HSBC = r"Your.HSBC.*eStatement"
