import re
from enum import Enum
from functools import cached_property
from typing import Any

from strenum import StrEnum


# pylint: disable=unused-argument,no-self-argument
class AutoEnum(StrEnum):
    """Generates lower case values for enums e.g. CITIBANK -> citibank."""

    def _generate_next_value_(self: str, *_):  # type: ignore[override]
        return self.lower()


class RegexEnum(Enum):
    """A subclass of `Enum` that converts member to a compiled regular expression pattern."""

    def __new__(cls, pattern):
        """
        Create a new `RegexEnum` member.

        Args:
        ----
            pattern (str): A regular expression pattern.

        """
        if not isinstance(pattern, str):
            msg = f"Pattern must be a string, not {type(pattern)}"
            raise TypeError(msg)

        obj = object.__new__(cls)
        obj._value_ = pattern
        return obj

    @cached_property
    def regex(self):
        return re.compile(self.value)

    def __str__(self):
        return self.value

    def match(self, value) -> re.Match:
        return self.regex.search(value)

    def findall(self, value) -> list[Any]:
        return self.regex.findall(value)

    def finditer(self, value) -> list[re.Match]:
        return self.regex.finditer(value)

    def search(self, value) -> re.Match:
        return self.regex.search(value)
