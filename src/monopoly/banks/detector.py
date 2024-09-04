import logging
from dataclasses import Field, fields
from functools import cached_property
from typing import TYPE_CHECKING, Any, Type

from monopoly.identifiers import Identifier, TextIdentifier
from monopoly.pdf import PdfDocument

if TYPE_CHECKING:
    from .base import BankBase

logger = logging.getLogger(__name__)


class BankDetector:
    def __init__(self, document: PdfDocument):
        self.document = document

    @cached_property
    def metadata_items(self) -> list[Any]:
        """
        Retrieves encryption and metadata identifiers from a bank statement PDF
        """
        identifiers: list[Identifier] = []
        if metadata_identifier := self.document.metadata_identifier:
            identifiers.append(metadata_identifier)

        if not identifiers:
            raise ValueError("Could not get identifier")

        return identifiers

    def detect_bank(self, banks: list[Type["BankBase"]]) -> Type["BankBase"] | None:
        """
        Reads the encryption metadata or actual metadata (if the PDF is not encrypted),
        and checks for a bank based on unique identifiers.
        """
        if not banks:
            banks = []

        logger.debug("Found PDF properties: %s", self.metadata_items)

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
            pdf_property_identifiers = list(
                filter(lambda i: not isinstance(i, TextIdentifier), grouped_identifiers)
            )

            if pdf_property_identifiers:
                if len(self.metadata_items) != len(pdf_property_identifiers):
                    continue

                if not self.pdf_properties_match(pdf_property_identifiers):
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

    def pdf_properties_match(
        self,
        grouped_identifiers: list[Identifier],
    ) -> bool:
        """
        Checks if all identifiers in the group match at least one metadata item.
        """
        for identifier in grouped_identifiers:
            matching_metadata = [
                metadata
                for metadata in self.metadata_items
                if type(metadata) is type(identifier)
            ]

            if not any(
                self.check_matching_identifier(metadata, identifier)
                for metadata in matching_metadata
            ):
                return False
        return True

    def check_matching_identifier(
        self,
        metadata: Identifier,
        identifier: Identifier,
    ) -> bool:
        """
        Checks if all fields in the metadata match the corresponding identifier fields.
        """
        return all(
            self.check_matching_field(field, metadata, identifier)
            for field in fields(metadata)
        )

    def check_matching_field(
        self,
        dataclass_field: Field,
        metadata: Identifier,
        identifier: Identifier,
    ) -> bool:
        """
        Checks if a field in the metadata matches the corresponding identifier field.
        """
        field_value = getattr(metadata, dataclass_field.name)
        identifier_value = getattr(identifier, dataclass_field.name)

        # if identifier is empty, we assume a match
        # this means only the identifiers in the bank
        # class need to be matched.
        if not identifier_value:
            return True

        # support partial string matching
        if isinstance(field_value, str) and isinstance(identifier_value, str):
            return identifier_value in field_value and identifier_value != ""

        # if not a string, only support exact match
        return identifier_value == field_value
