from dataclasses import fields
from typing import TYPE_CHECKING

from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from monopoly.banks.detector import BankDetector


@dataclass(frozen=True)
class Identifier:
    """Parent class for identifiers, used for type hinting."""

    def matches(self, detector: "BankDetector") -> bool:
        """Check if this identifier is found in the parsed document context."""
        raise NotImplementedError


@dataclass(frozen=True)
class MetadataIdentifier(Identifier):
    """Stores the metadata attributes of a PDF."""

    format: str = ""
    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    producer: str = ""

    def matches(self, detector: "BankDetector") -> bool:
        """Check for partial matches against the document's metadata."""
        document_metadata = detector.metadata_identifier
        for field in fields(self):
            # The value from the bank config (e.g. format="PDF 1.6")
            config_value = getattr(self, field.name)
            # The value from the parsed document
            document_value = getattr(document_metadata, field.name)

            # We only check fields that are actually defined in the config
            if not config_value:
                continue

            # The document must have a value to compare against
            if not document_value:
                return False

            # The configured value must be a substring of the document's value
            if config_value not in document_value:
                return False

        return True


@dataclass(frozen=True)
class TextIdentifier(Identifier):
    """Stores a specific string that exists in the content of a PDF."""

    text: str = ""

    def matches(self, detector: "BankDetector") -> bool:
        """Check if the identifier's text exists in the document's raw text."""
        # Ensure the document has raw text before checking
        if not detector.document.raw_text:
            return False
        return self.text in detector.document.raw_text
