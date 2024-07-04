import logging
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

import fitz

from monopoly.banks import detect_bank
from monopoly.constants import EncryptionIdentifier, Identifier, MetadataIdentifier
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


class MetadataAnalyzer:
    def __init__(self, document: PdfDocument):
        self.document = document

    @property
    def bank(self):
        return detect_bank(self.metadata_items)

    @property
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
            logger.debug("Found metadata identifier: %s", metadata_identifier)
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
