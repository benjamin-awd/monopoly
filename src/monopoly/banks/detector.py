import logging
from typing import TYPE_CHECKING, Type

from monopoly.identifiers import MetadataIdentifier, TextIdentifier
from monopoly.pdf import PdfDocument

if TYPE_CHECKING:
    from .base import BankBase

logger = logging.getLogger(__name__)


class BankDetector:
    def __init__(self, document: PdfDocument):
        self.document = document
        self.metadata_identifier = document.metadata_identifier

    def detect_bank(self, banks: list[Type["BankBase"]]) -> Type["BankBase"] | None:
        """
        Reads the encryption metadata or actual metadata (if the PDF is not encrypted),
        and checks for a bank based on unique identifiers.
        """
        if not banks:
            banks = []

        logger.debug("Found PDF properties: %s", self.metadata_identifier)

        for bank in banks:
            if self.is_bank_identified(bank):
                return bank
        return None

    def is_bank_identified(
        self,
        bank: Type["BankBase"],
    ) -> bool:
        """
        Checks if a bank is identified based on a list of metadata items.
        """
        for grouped_identifiers in bank.identifiers:  # type: ignore
            text_identifiers = list(
                filter(lambda i: isinstance(i, TextIdentifier), grouped_identifiers)
            )
            metadata_identifiers = list(
                filter(lambda i: isinstance(i, MetadataIdentifier), grouped_identifiers)
            )

            if metadata_identifiers:
                if not self.metadata_identifiers_match(metadata_identifiers):
                    continue

                if not self.text_identifiers_match(text_identifiers):
                    logger.warning("PDF metadata matches but text not found")
                    return False

                logger.debug("Identified statement bank: %s", bank.__name__)
                return True

            if text_identifiers:
                if self.text_identifiers_match(text_identifiers):
                    return True

        return False

    def text_identifiers_match(self, text_identifiers: list[TextIdentifier]) -> bool:
        if not text_identifiers:
            return True

        for identifier in text_identifiers:
            if identifier.text not in self.document.raw_text:
                return False

        logger.debug("Text identifier found in PDF")
        return True

    def metadata_identifiers_match(
        self, bank_metadata_identifiers: list[MetadataIdentifier]
    ) -> bool:
        for identifier in bank_metadata_identifiers:
            if self.metadata_identifier.matches(identifier):
                return True
        return False
