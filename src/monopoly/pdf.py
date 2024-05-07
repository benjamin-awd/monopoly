import logging
from dataclasses import dataclass
from functools import cached_property
from io import BytesIO
from pathlib import Path
from typing import Optional

import fitz
import pdftotext
from pdf2john import PdfHashExtractor as EncryptionMetadataExtractor
from pydantic import SecretStr

from monopoly.config import PdfConfig

logger = logging.getLogger(__name__)


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
        file_path: Optional[Path] = None,
        file_bytes: Optional[bytes] = None,
        pdf_config: Optional[PdfConfig] = None,
    ):
        """
        Class responsible for parsing PDFs and returning raw text

        The page_range variable determines which pages are extracted.
        All pages are extracted by default.
        """
        self.file_path = file_path
        self.file_bytes = file_bytes

        if pdf_config is None:
            pdf_config = PdfConfig()

        self.passwords = pdf_config.passwords
        self.page_range = slice(*pdf_config.page_range)
        self.page_bbox = pdf_config.page_bbox

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

    def get_metadata(self) -> dict:
        """
        Extracts metadata from the PDF document.
        """
        document = self.open()
        metadata = document.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": str(metadata.get("creationDate", "")),
            "modification_date": str(metadata.get("modDate", "")),
        }

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
        if self.file_path:
            return fitz.Document(filename=self.file_path)

        if self.file_bytes:
            return fitz.Document(stream=self.file_bytes)

        raise RuntimeError("Either file path or file bytestream must be passed")

    @cached_property
    def extractor(self) -> EncryptionMetadataExtractor:
        """
        Returns an instance of pdf2john, used to retrieve and return
        the encryption metadata from a PDF's encryption dictionary
        """
        if self.file_path:
            return EncryptionMetadataExtractor(file_name=self.file_path)

        if self.file_bytes:
            return EncryptionMetadataExtractor(file_bytes=self.file_bytes)

        raise RuntimeError("Either file path or file bytestream must be passed")

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
