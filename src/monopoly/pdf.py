import logging
from dataclasses import dataclass
from functools import cached_property, lru_cache
from io import BytesIO
from pathlib import Path
from typing import Optional, Type

import fitz
import pdftotext
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from monopoly.banks import BankBase

logger = logging.getLogger(__name__)


class MissingOCRError(Exception):
    """
    Error that is raised when PDF does not contain any selectable text
    """


class PdfPasswords(BaseSettings):
    """
    Pydantic model that automatically populates variables from a .env file,
    or an environment variable called `PDF_PASSWORDS`.
    e.g. export PDF_PASSWORDS='["password123", "secretpass"]'
    """

    pdf_passwords: list[SecretStr] = [SecretStr("")]
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


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


class PdfDocument:
    """Handles logic related to the opening, unlocking and storage of a PDF document"""

    def __init__(
        self,
        passwords: Optional[list[SecretStr]] = None,
        file_path: Optional[Path] = None,
        file_bytes: Optional[bytes] = None,
    ):
        self._passwords = passwords
        self.file_path = file_path
        self.file_bytes = file_bytes

    @cached_property
    def raw_text(self) -> str:
        raw_text = ""
        for page in self.open():
            raw_text += page.get_text()
        return raw_text

    @property
    def passwords(self):
        if not self._passwords:
            return PdfPasswords().pdf_passwords
        return self._passwords

    @cached_property
    def name(self):
        return self.open().name

    @cached_property
    def metadata(self):
        return self.open().metadata

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

    @lru_cache
    def get_byte_stream(self) -> BytesIO:
        if self.file_path:
            with open(self.file_path, "rb") as file:
                stream = BytesIO(file.read())
            return stream

        if self.file_bytes:
            return BytesIO(self.file_bytes)

        raise RuntimeError("Unable to create document")

    @lru_cache
    def open(self) -> fitz.Document:
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


class PdfParser:
    def __init__(self, bank: Type[BankBase], document: PdfDocument):
        """
        Class responsible for parsing PDFs and returning raw text

        The page_range variable determines which pages are extracted.
        All pages are extracted by default.
        """
        self.bank = bank
        self.document = document

    @property
    def pdf_config(self):
        return self.bank.pdf_config

    @cached_property
    def page_range(self):
        return slice(*self.pdf_config.page_range)

    @cached_property
    def page_bbox(self):
        return self.pdf_config.page_bbox

    @lru_cache
    def get_pages(self) -> list[PdfPage]:
        logger.debug("Extracting text from PDF")
        document = self.document.open()

        num_pages = list(range(document.page_count))
        document.select(num_pages[self.page_range])

        if cropbox := self.page_bbox:
            logger.debug(
                "Will crop pages with crop box %s and remove vertical text", cropbox
            )
        for page in document:
            if self.page_bbox:
                page.set_cropbox(cropbox)
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

                # assume PDF is missing OCR if text is less than 10 chars on every page
                if all(len(page) < 10 for page in pdf):
                    raise MissingOCRError("No selectable text found")

                return [PdfPage(page) for page in pdf]
            except pdftotext.Error:
                continue
        raise RuntimeError("Unable to retrieve pages")

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
