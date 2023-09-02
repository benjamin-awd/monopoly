from enum import Enum


class BankStatement(str, Enum):
    DATE = "date"
    DESCRIPTION = "description"
    AMOUNT = "amount"


class EmailSubject(str, Enum):
    OCBC_365 = "OCBC Bank: Your Credit Card e-Statement"
    HSBC_REVOLUTION = "Your HSBC VISA REVOLUTION eStatement"
