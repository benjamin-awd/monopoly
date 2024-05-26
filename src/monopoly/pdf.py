import logging
from dataclasses import dataclass, field
from functools import cached_property, lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

import fitz
import pdftotext
from pydantic import SecretStr

from monopoly.banks import detect_bank
from monopoly.constants import EncryptionIdentifier, MetadataIdentifier

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


@dataclass
class PdfPage:
    """
    Dataclass representation of a bank statement PDF page.
    Contains the raw text of a PDF page, and allows access
    to the raw text as a list via the `lines` property
    """

    raw_text: str

    @cached_property
    def lines(self) -> list[str]:
        return self.raw_text.split("\n")


class WrongPasswordError(Exception):
    """Exception raised when an incorrect password is provided"""


class MissingPasswordError(Exception):
    """Exception raised when the document is encrypted, but no password is provided"""


class BadPasswordFormatError(Exception):
    """Exception raised passwords are not provided in a proper format"""


class PdfParser:
    def __init__(
        self,
        passwords: Optional[list[SecretStr]] = None,
        file_path: Optional[Path] = None,
        file_bytes: Optional[bytes] = None,
    ):
        """
        Class responsible for parsing PDFs and returning raw text

        The page_range variable determines which pages are extracted.
        All pages are extracted by default.
        """
        self._passwords = passwords
        self.file_path = file_path
        self.file_bytes = file_bytes

    @property
    def bank(self):
        return detect_bank(self.metadata_items)

    @property
    def passwords(self):
        if not self._passwords:
            return self.bank.passwords
        return self._passwords

    @property
    def pdf_config(self):
        return self.bank.pdf_config

    @cached_property
    def page_range(self):
        return slice(*self.pdf_config.page_range)

    @cached_property
    def page_bbox(self):
        return self.pdf_config.page_bbox

    @property
    def metadata_items(self) -> list[Any]:
        """
        Retrieves encryption and metadata identifiers from a bank statement PDF
        """
        identifiers = []
        # pylint: disable=protected-access
        if encrypt_dict := self.encrypt_dict:
            encryption_identifier = EncryptionIdentifier(
                float(encrypt_dict.pdf_version),
                encrypt_dict.algorithm,
                encrypt_dict.revision,
                encrypt_dict.length,
                encrypt_dict.permissions,
            )
            identifiers.append(encryption_identifier)

        if metadata := self.document.metadata:
            metadata_identifier = MetadataIdentifier(**metadata)
            identifiers.append(metadata_identifier)  # type: ignore

        if not identifiers:
            raise ValueError("Could not get identifier")

        return identifiers

    def open(self):
        """
        Opens and decrypts a PDF document
        """
        document = self.document

        if not document.is_encrypted:
            return document

        if not self.passwords:
            raise MissingPasswordError("No password found in PDF configuration")

        if not any(str(password) for password in self.passwords):
            raise MissingPasswordError("Password in PDF configuration is empty")

        if not isinstance(self.passwords, list):
            raise BadPasswordFormatError("Passwords should be stored in a list")

        if not all(isinstance(item, SecretStr) for item in self.passwords):
            raise BadPasswordFormatError("Passwords should be stored as SecretStr")

        for password in self.passwords:
            document.authenticate(password.get_secret_value())

            if not document.is_encrypted:
                logger.debug("Successfully authenticated with password")
                return document
        raise WrongPasswordError(f"Could not open document: {document.name}")

    @lru_cache
    def get_pages(self) -> list[PdfPage]:
        logger.debug("Extracting text from PDF")
        document: fitz.Document = self.open()

        num_pages = list(range(document.page_count))
        document.select(num_pages[self.page_range])

        for page in document:
            if self.page_bbox:
                logger.debug("Cropping page")
                page.set_cropbox(self.page_bbox)

            logger.debug("Removing vertical text")
            page = self._remove_vertical_text(page)

        # certain statements require garbage collection, so that duplicate objects
        # do not cause pdftotext to fail due to missing xrefs/null values
        # however, setting `garbage=2` may cause issues with other statements
        # so an initial attempt should be made to run using `garbage=0`
        garbage_values = [0, 2]

        for garbage in garbage_values:
            try:
                pdf_byte_stream = BytesIO(document.tobytes(garbage=garbage))
                pdf = pdftotext.PDF(pdf_byte_stream, physical=True)
                return [PdfPage(page) for page in pdf]
            except pdftotext.Error:
                continue
        raise RuntimeError("Unable to retrieve pages")

    @cached_property
    def document(self) -> fitz.Document:
        """
        Returns a Python representation of a PDF document.
        """
        if not self.file_path and not self.file_bytes:
            raise RuntimeError("Either `file_path` or `file_bytes` must be passed")

        if self.file_path and self.file_bytes:
            raise RuntimeError(
                "Only one of `file_path` or `file_bytes` should be defined"
            )

        args = {"filename": self.file_path, "stream": self.file_bytes}
        return fitz.Document(**args)

    @cached_property
    def encrypt_dict(self) -> EncryptDict | None:
        stream = self._get_doc_byte_stream()
        pdf_version_string = stream.read(8).decode("utf-8", "backslashreplace")

        if self.document.is_encrypted:
            raw_encrypt_dict = self._get_raw_encrypt_dict(self.document)
            encrypt_dict = EncryptDict(raw_encrypt_dict, pdf_version_string)
            return encrypt_dict
        return None

    @staticmethod
    def _remove_vertical_text(page: fitz.Page):
        """Helper function to remove vertical text, based on writing direction (wdir).

        This helps avoid situations where the PDF is oddly parsed, due to vertical text
        inside the PDF.

        An example of vertical text breaking a transaction:
        ```
        'HEALTHY HARVEST CAFÉ SINGAPORE SG',
        'Co Reg No: 123456',
        '10 NOV 9.80',
        ```

        Note:
            The 'dir' key represents the tuple (cosine, sine) for the angle.
            If line["dir"] != (1, 0), the text of its spans is rotated.

        """
        for block in page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]:
            for line in block["lines"]:
                writing_direction = line["dir"]
                if writing_direction != (1, 0):
                    page.add_redact_annot(line["bbox"])
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
        return page

    @staticmethod
    def _get_raw_encrypt_dict(doc: fitz.Document) -> dict:
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

    def _get_doc_byte_stream(self) -> BytesIO:
        if self.file_path:
            with open(self.file_path, "rb") as file:
                stream = BytesIO(file.read())
            return stream
        raise RuntimeError("Unable to create stream since `file_path` not passed")
