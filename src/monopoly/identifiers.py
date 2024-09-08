from dataclasses import fields
from functools import lru_cache

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Identifier:
    """Parent class for identifiers, used for type hinting"""


@dataclass(frozen=True)
class MetadataIdentifier(Identifier):
    """Stores the metadata attributes of a PDF"""

    format: str = ""
    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    producer: str = ""

    @lru_cache
    def matches(self, other: "MetadataIdentifier") -> bool:
        """Check for partial matches on all string fields."""
        for field in fields(self):
            self_value = getattr(self, field.name)
            other_value = getattr(other, field.name)

            # Perform partial matching if both fields are non-empty strings
            if isinstance(self_value, str) and isinstance(other_value, str):
                if other_value and other_value not in self_value:
                    return False

        return True


@dataclass(frozen=True)
class TextIdentifier(Identifier):
    """Stores a specific string that exists in the content of a PDF"""

    text: str = ""

    @lru_cache
    def matches(self, raw_text: str) -> bool:
        """Check for partial matches on all string fields."""
        return self.text in raw_text
