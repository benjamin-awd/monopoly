import json
import re
from collections.abc import Mapping
from typing import Any

from pydantic import ConfigDict, Field, field_validator, model_validator
from pydantic.dataclasses import dataclass
from pydantic_core import ArgsKwargs

from monopoly.constants import Columns


# ruff: noqa: N805
class TransactionGroupDict(Mapping):
    """
    Helper class that holds the group dict from a match.

    This class acts as a convenient wrapper to allow unpacking into the
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
        transaction_date: str | None = None,
        polarity: str | None = None,
        **_,
    ):
        self.transaction_date = transaction_date
        self.amount = amount
        self.description = description
        self.polarity = polarity

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
    page_number: int

    def span(self):
        return self.match.span()


@dataclass
class Transaction:
    """
    Hold transaction data, validates the data, and performs various coercions.

    This includes removing whitespaces and commas, reassigning 'transaction_date' to 'date'
    """

    description: str
    amount: float
    date: str = Field(alias="transaction_date")
    polarity: str | None = None
    # avoid storing config logic, since the Transaction object is used to create
    # a single unique hash which should not change
    auto_polarity: bool = Field(default=True, init=True, repr=False)

    def as_raw_dict(self, *_, show_polarity=False):
        """Return stringified dictionary version of the transaction."""
        items = {
            Columns.DATE.value: self.date,
            Columns.DESCRIPTION.value: self.description,
            Columns.AMOUNT.value: str(self.amount),
        }
        if show_polarity:
            items[Columns.POLARITY] = self.polarity
        return items

    @field_validator("description", mode="after")
    def remove_extra_whitespace(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator(Columns.AMOUNT, mode="before")
    def prepare_amount_for_float_coercion(cls, amount: str) -> str:
        """
        Replace commas, whitespaces, apostrophes and parentheses for string representation of floats.

        1'234.00 -> 1234.00
        1,234.00 -> 1234.00
        (-10.00) -> -10.00
        (-1.56 ) -> -1.56.
        """
        if isinstance(amount, str):
            return re.sub(r"[,)(\s']", "", amount)
        return amount

    # pylint: disable=bad-classmethod-argument
    @model_validator(mode="before")
    def treat_parenthesis_enclosure_as_credit(self: ArgsKwargs | Any) -> "ArgsKwargs":
        """Treat amounts enclosed by parentheses (e.g. cashback) as a credit entry."""
        if self.kwargs:
            amount: str = self.kwargs[Columns.AMOUNT]
            if isinstance(amount, str) and amount.startswith("(") and amount.endswith(")"):
                self.kwargs[Columns.POLARITY] = "CR"
        return self

    @model_validator(mode="after")
    def convert_credit_amount_to_negative(self: "Transaction") -> "Transaction":
        """Convert transactions with a polarity of "CR" or "+" to positive."""
        # avoid negative zero
        if self.amount == 0:
            return self

        if not self.auto_polarity:
            return self

        if self.polarity in ("CR", "+"):
            self.amount = abs(self.amount)

        else:
            self.amount = -abs(self.amount)
        return self

    def __str__(self):
        return json.dumps(self.as_raw_dict(show_polarity=True))
