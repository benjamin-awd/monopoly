"""This file stores configuration related constants and patterns"""

from enum import auto

from monopoly.constants.enums import AutoEnum


class EntryType(AutoEnum):
    CREDIT = auto()
    DEBIT = auto()


class BankNames(AutoEnum):
    CITIBANK = auto()
    DBS = auto()
    HSBC = auto()
    MAYBANK = auto()
    OCBC = auto()
    STANDARD_CHARTERED = auto()


class InternalBankNames(AutoEnum):
    EXAMPLE = auto()
    GENERIC = auto()


class Columns(AutoEnum):
    AMOUNT = auto()
    DATE = auto()
    DESCRIPTION = auto()
    SUFFIX = auto()
    TRANSACTION_DATE = auto()
