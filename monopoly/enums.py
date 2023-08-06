from enum import Enum


class BankStatement(str, Enum):
    DATE = "Date"
    DESCRIPTION = "Description"
    AMOUNT = "Amount"
