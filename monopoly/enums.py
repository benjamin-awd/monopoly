from enum import Enum


class BankStatement(str, Enum):
    DATE = "date"
    DESCRIPTION = "description"
    AMOUNT = "amount"
