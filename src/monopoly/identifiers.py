from pydantic.dataclasses import dataclass


@dataclass
class Identifier:
    """Parent class for identifiers, used for type hinting"""


@dataclass
class MetadataIdentifier(Identifier):
    """Stores the metadata attributes of a PDF"""

    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    producer: str = ""


@dataclass
class TextIdentifier(Identifier):
    """Stores a specific string that exists in the content of a PDF"""

    text: str = ""
