"""This file stores configuration related constants and patterns"""

from enum import auto

from strenum import StrEnum


# pylint: disable=unused-argument,no-self-argument
class AutoEnum(StrEnum):
    """Generates lower case values for enums
    e.g. CITIBANK -> citibank
    """

    def _generate_next_value_(name: str, *_):  # type: ignore
        return name.lower()


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
