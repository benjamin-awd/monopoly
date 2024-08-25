import re
from enum import Enum
from functools import cached_property
from typing import Any

from strenum import StrEnum


# pylint: disable=unused-argument,no-self-argument
class AutoEnum(StrEnum):
    """Generates lower case values for enums
    e.g. CITIBANK -> citibank
    """

    def _generate_next_value_(name: str, *_):  # type: ignore
        return name.lower()


class RegexEnum(Enum):
    """
    A subclass of `Enum` that converts member to a compiled
    regular expression pattern.
    """

    def __new__(cls, pattern):
        """
        Create a new `RegexEnum` member.

        Args:
            pattern (str): A regular expression pattern.
        """
        if not isinstance(pattern, str):
            raise TypeError(f"Pattern must be a string, not {type(pattern)}")

        obj = object.__new__(cls)
        obj._value_ = pattern
        return obj

    @cached_property
    def regex(self):
        return re.compile(self.value)

    def __str__(self):
        return self.value

    def match(self, value) -> re.Match:
        """
        Wrapper for re.match
        """
        return self.regex.search(value)

    def findall(self, value) -> list[Any]:
        """
        Wrapper for re.findall
        """
        return self.regex.findall(value)

    def finditer(self, value) -> list[re.Match]:
        """
        Wrapper for re.finditer
        """
        return self.regex.finditer(value)

    def search(self, value) -> re.Match:
        """
        Wrapper for re.search
        """
        return self.regex.search(value)
