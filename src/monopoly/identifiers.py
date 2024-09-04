from dataclasses import fields

from pydantic.dataclasses import dataclass


@dataclass
class Identifier:
    """Parent class for identifiers, used for type hinting"""


@dataclass
class MetadataIdentifier(Identifier):
    """Stores the metadata attributes of a PDF"""

    format: str = ""
    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    producer: str = ""

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


@dataclass
class TextIdentifier(Identifier):
    """Stores a specific string that exists in the content of a PDF"""

    text: str = ""
