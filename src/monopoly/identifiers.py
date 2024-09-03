from dataclasses import dataclass


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
    keywords: str = ""
    creationDate: str = ""
    modDate: str = ""
    trapped: str = ""
    encryption: dict = None


@dataclass
class TextIdentifier(Identifier):
    """Stores a specific string that exists in the content of a PDF"""

    text: str = ""
