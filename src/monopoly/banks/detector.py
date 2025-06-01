import logging
from typing import TYPE_CHECKING

from monopoly.identifiers import MetadataIdentifier, TextIdentifier
from monopoly.pdf import PdfDocument

if TYPE_CHECKING:
    from .base import BankBase

logger = logging.getLogger(__name__)


class BankDetector:
    def __init__(self, document: PdfDocument):
        self.document = document
        self.metadata_identifier = document.metadata_identifier

    def detect_bank(self, banks: list[type["BankBase"]]) -> type["BankBase"] | None:
        """Detect the bank using encryption metadata or actual metadata."""
        if not banks:
            banks = []

        logger.debug("Found PDF properties: %s", self.metadata_identifier)

        for bank in banks:
            if self.is_bank_identified(bank):
                return bank
        return None

    def is_bank_identified(
        self,
        bank: type["BankBase"],
    ) -> bool:
        """Check if a bank is identified based on a list of metadata items."""
        for grouped_identifiers in bank.identifiers:
            if self.identifiers_match(grouped_identifiers):
                logger.debug("Identified statement bank: %s", bank.__name__)
                return True

        return False

    def text_identifiers_match(self, text_identifiers: list[TextIdentifier]) -> bool:
        if not text_identifiers:
            return True

        for identifier in text_identifiers:
            if not identifier.matches(self.document.raw_text):
                return False

        logger.debug("Text identifier found in PDF")
        return True

    def metadata_identifiers_match(self, bank_metadata_identifiers: list[MetadataIdentifier]) -> bool:
        return any(self.metadata_identifier.matches(identifier) for identifier in bank_metadata_identifiers)

    def identifiers_match(self, identifiers: list) -> bool:
        text_identifiers = self.get_identifiers_of_type(identifiers, TextIdentifier)
        metadata_identifiers = self.get_identifiers_of_type(identifiers, MetadataIdentifier)

        if metadata_identifiers:
            if not self.metadata_identifiers_match(metadata_identifiers):
                return False
            if not self.text_identifiers_match(text_identifiers):
                return False

        return self.text_identifiers_match(text_identifiers)

    def get_identifiers_of_type(self, identifiers: list, identifier_type: type) -> list:
        return [i for i in identifiers if isinstance(i, identifier_type)]
