import json
import re
from collections.abc import Mapping
from typing import Any, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator
from pydantic.dataclasses import dataclass
from pydantic_core import ArgsKwargs

from monopoly.constants import Columns


class TransactionGroupDict(Mapping):
    """
    Helper class that holds the group dict from a match. This
    class acts as a convenient wrapper to allow unpacking into the
    `Transaction` class.

    A transaction should at minimum always have a description and amount

    In cases where we parse a previous balance line, the date might not exist
    e.g.
    `          LAST MONTH'S BALANCE         6,321`
    `01 OCT    ValueVille                  123.12`
    """

    def __init__(
        self,
        description: str,
        amount: str,
        transaction_date: Optional[str] = None,
        suffix: Optional[str] = None,
        **_,
    ):
        self.transaction_date = transaction_date
        self.amount = amount
        self.description = description
        self.suffix = suffix

    def __getitem__(self, x):
        return self.__dict__[x]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def asdict(self):
        return self.__dict__

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return (
            "<TransactionGroupDict object; "
            f"{Columns.TRANSACTION_DATE}={self.transaction_date}, "
            f"{Columns.AMOUNT}={self.amount}, "
            f"{Columns.DESCRIPTION}={self.description}>"
        )


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class TransactionMatch:
    groupdict: TransactionGroupDict
    match: re.Match

    def span(self):
        return self.match.span()


@dataclass
class Transaction:
    """
    Holds transaction data, validates the data, and
    performs various coercions like removing whitespaces
    and commas.

    Reassigns 'transaction_date' to 'date'
    """

    description: str
    amount: float
    date: str = Field(alias="transaction_date")
    suffix: Optional[str] = None

    def as_raw_dict(self, show_suffix=False):
        """Returns stringified dictionary version of the transaction"""
        items = {
            Columns.DATE.value: self.date,
            Columns.DESCRIPTION.value: self.description,
            Columns.AMOUNT.value: str(self.amount),
        }
        if show_suffix:
            items[Columns.SUFFIX] = self.suffix
        return items

    @field_validator("description", mode="after")
    def remove_extra_whitespace(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator(Columns.AMOUNT, mode="before")
    def prepare_amount_for_float_coercion(cls, amount: str) -> str:
        """
        Replaces commas, whitespaces and parentheses in string representation of floats
        e.g.
            1,234.00 -> 1234.00
            (-10.00) -> -10.00
            (-1.56 ) -> -1.56
        """
        if isinstance(amount, str):
            return re.sub(r"[,)(\s]", "", amount)
        return amount

    # pylint: disable=bad-classmethod-argument
    @model_validator(mode="before")  # type: ignore
    def treat_parenthesis_enclosure_as_credit(self: ArgsKwargs | Any) -> "ArgsKwargs":
        """
        Treat amounts enclosed by parentheses (e.g. cashback) as a credit entry
        """
        if self.kwargs:
            amount: str = self.kwargs[Columns.AMOUNT]
            if isinstance(amount, str):
                if amount.startswith("(") and amount.endswith(")"):
                    self.kwargs[Columns.SUFFIX] = "CR"
        return self

    @model_validator(mode="after")
    def convert_credit_amount_to_negative(self: "Transaction") -> "Transaction":
        """
        Converts transactions with a suffix of "CR" or "+" to positive
        """
        if self.suffix in ("CR", "+"):
            self.amount = abs(self.amount)

        else:
            self.amount = -abs(self.amount)
        return self

    def __str__(self):
        return json.dumps(self.as_raw_dict(show_suffix=True))
