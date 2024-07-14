import logging
from dataclasses import Field, dataclass, field, fields
from functools import cached_property
from typing import Any, Type

import fitz

from monopoly.banks import BankBase, banks
from monopoly.identifiers import (
    EncryptionIdentifier,
    Identifier,
    MetadataIdentifier,
    TextIdentifier,
)
from monopoly.pdf import PdfDocument

logger = logging.getLogger(__name__)


@dataclass
class EncryptDict:
    """Stores encryption dictionary of a PDF"""

    raw_encrypt_dict: dict
    pdf_version: str
    algorithm: int = field(init=False)
    length: int = field(init=False)
    permissions: int = field(init=False)
    revision: int = field(init=False)

    def __post_init__(self):
        self.pdf_version = float(self.pdf_version[-3:])
        self.algorithm = int(self.raw_encrypt_dict.get("V"))
        self.length = int(self.raw_encrypt_dict.get("Length"))
        self.permissions = int(self.raw_encrypt_dict.get("P"))
        self.revision = int(self.raw_encrypt_dict.get("R"))


class BankDetector:
    def __init__(self, document: PdfDocument):
        self.document = document

    @cached_property
    def metadata_items(self) -> list[Any]:
        """
        Retrieves encryption and metadata identifiers from a bank statement PDF
        """
        identifiers: list[Identifier] = []
        if encrypt_dict := self.encrypt_dict:
            encryption_identifier = EncryptionIdentifier(
                float(encrypt_dict.pdf_version),
                encrypt_dict.algorithm,
                encrypt_dict.revision,
                encrypt_dict.length,
                encrypt_dict.permissions,
            )
            logger.debug("Found encryption identifier: %s", encryption_identifier)
            identifiers.append(encryption_identifier)

        if metadata := self.document.open().metadata:
            metadata_identifier = MetadataIdentifier(**metadata)
            identifiers.append(metadata_identifier)

        if not identifiers:
            raise ValueError("Could not get identifier")

        return identifiers

    @cached_property
    def encrypt_dict(self) -> EncryptDict | None:
        document = self.document.open()
        stream = self.document.get_byte_stream()
        pdf_version_string = stream.read(8).decode("utf-8", "backslashreplace")
        try:
            raw_encrypt_dict = self.get_raw_encrypt_dict(document)
            encrypt_dict = EncryptDict(raw_encrypt_dict, pdf_version_string)
            return encrypt_dict
        except TypeError:
            return None

    @staticmethod
    def get_raw_encrypt_dict(doc: fitz.Document) -> dict:
        """
        Helper function to extract the PDF encryption dictionary, since
        `fitz` doesn't provide it
        """
        encrypt_metadata = {}
        pdf_object, value = doc.xref_get_key(-1, "Encrypt")
        if pdf_object != "xref":
            pass  # PDF has no metadata
        else:
            xref = int(value.replace("0 R", ""))  # extract the metadata xref
            for key in doc.xref_get_keys(xref):
                encrypt_metadata[key] = doc.xref_get_key(xref, key)[1]
        return encrypt_metadata

    def detect_bank(self) -> Type[BankBase] | None:
        """
        Reads the encryption metadata or actual metadata (if the PDF is not encrypted),
        and checks for a bank based on unique identifiers.
        """
        logger.debug("Found PDF properties: %s", self.metadata_items)

        for bank in banks:
            if self.is_bank_identified(bank):
                return bank
        return None

    def is_bank_identified(
        self,
        bank: Type[BankBase],
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

            if pdf_property_identifiers and len(self.metadata_items) != len(
                pdf_property_identifiers
            ):
                continue

            if self.pdf_properties_match(pdf_property_identifiers):
                if not self.text_identifiers_match(text_identifiers):
                    logger.warning("PDF metadata matches but text not found")
                    return False

                logger.debug("Identified statement bank: %s", bank.__name__)
                return True

            # support for statements that only have text identifiers
            if text_identifiers and self.text_identifiers_match(text_identifiers):
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
