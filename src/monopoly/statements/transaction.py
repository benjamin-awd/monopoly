import json
import re
from dataclasses import dataclass, field
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic_core import ArgsKwargs

from monopoly.constants import Columns


# ruff: noqa: N805
@dataclass
class RawTransaction:
    """
    Intermediate transaction data during the parsing pipeline.

    Holds both the extracted transaction fields and parse context
    (regex match object, page number) needed for processing.
    """

    # Transaction fields
    description: str
    amount: str
    transaction_date: str | None = None
    polarity: str | None = None
    balance: str | None = None

    # Parse context
    match: re.Match | None = field(default=None)
    page_number: int = 0

    def as_dict(self) -> dict[str, Any]:
        """Return transaction fields as dict for unpacking into Transaction."""
        return {
            "description": self.description,
            "amount": self.amount,
            "transaction_date": self.transaction_date,
            "polarity": self.polarity,
            "balance": self.balance,
        }

    def span(self):
        """Return the span of the regex match."""
        return self.match.span()


@pydantic_dataclass
class Transaction:
    """
    Hold transaction data, validates the data, and performs various coercions.

    This includes removing whitespaces and commas, reassigning 'transaction_date' to 'date'
    """

    description: str
    amount: float
    date: str = Field(alias="transaction_date")
    polarity: str | None = None
    balance: float = Field(default=0)
    # avoid storing config logic, since the Transaction object is used to create
    # a single unique hash which should not change
    auto_polarity: bool = Field(default=True, init=True, repr=False)

    def as_raw_dict(self, *_, show_polarity=False, show_balance=False):
        """Return stringified dictionary version of the transaction."""
        items = {
            Columns.DATE.value: self.date,
            Columns.DESCRIPTION.value: self.description,
            Columns.AMOUNT.value: str(self.amount),
        }
        if show_polarity and self.polarity is not None:
            items[Columns.POLARITY.value] = self.polarity
        if show_balance:
            items[Columns.BALANCE.value] = str(self.balance)
        return items

    @field_validator("description", mode="after")
    def remove_extra_whitespace(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator(Columns.AMOUNT, Columns.BALANCE, mode="before")
    def prepare_for_float_coercion(cls, value: str | None) -> str:
        """
        Replace commas, whitespaces, apostrophes and parentheses for string representation of floats.

        1'234.00 -> 1234.00
        1,234.00 -> 1234.00
        (-10.00) -> -10.00
        (-1.56 ) -> -1.56.
        """
        if value is None:
            return "0"
        if isinstance(value, str):
            return re.sub(r"[^\d\.\-]", "", value)
        return str(value)

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
