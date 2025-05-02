import logging
from dataclasses import dataclass
from functools import cached_property, lru_cache
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Type

import pdftotext
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymupdf import TEXTFLAGS_TEXT, Document, Page

from monopoly.identifiers import MetadataIdentifier

if TYPE_CHECKING:
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


class PdfDocument(Document):
    """Handles logic related to the opening, unlocking, and storage of a PDF document."""

    def __init__(
        self,
        file_path: Optional[Path] = None,
        file_bytes: Optional[bytes | BytesIO] = None,
        passwords: Optional[list[SecretStr]] = None,
    ):
        self.file_path = file_path
        self.file_bytes = file_bytes
        self.passwords = passwords or PdfPasswords().pdf_passwords

        if not any([self.file_path, self.file_bytes]):
            raise RuntimeError("Either `file_path` or `file_bytes` must be passed")

        if self.file_path and self.file_bytes:
            raise RuntimeError(
                "Only one of `file_path` or `file_bytes` should be passed"
            )

        args = {"filename": self.file_path, "stream": self.file_bytes}
        super().__init__(**args)

    @cached_property
    def metadata_identifier(self):
        return MetadataIdentifier(**self.metadata)

    def unlock_document(self):
        """Attempt to unlock the document using the provided passwords."""
        if not self.is_encrypted:
            return self

        if not self.passwords:
            raise MissingPasswordError("No password found in PDF configuration")

        if not any(str(password) for password in self.passwords):
            raise MissingPasswordError("Password in PDF configuration is empty")

        if not isinstance(self.passwords, list):
            raise BadPasswordFormatError("Passwords should be stored in a list")

        if not all(isinstance(item, SecretStr) for item in self.passwords):
            raise BadPasswordFormatError("Passwords should be stored as SecretStr")

        for password in self.passwords:
            if self.authenticate(password.get_secret_value()):
                logger.debug("Successfully authenticated with password")
                return self

        raise WrongPasswordError(f"Could not open document: {self.name}")

    @cached_property
    def raw_text(self) -> str:
        """Extracts and returns the text from the PDF"""
        raw_text = ""
        for page in self:
            raw_text += page.get_text()
        return raw_text


class PdfParser:
    def __init__(
        self,
        bank: Type["BankBase"],
        document: PdfDocument,
    ):
        """
        Class responsible for parsing PDFs and returning raw text

        The page_range variable determines which pages are extracted.
        All pages are extracted by default.
        """
        self.bank = bank
        self.document = document
        self.metadata_identifier = document.metadata_identifier

    @property
    def pdf_config(self):
        return self.bank.pdf_config

    @cached_property
    def page_range(self):
        return slice(*self.pdf_config.page_range)

    @cached_property
    def page_bbox(self):
        return self.pdf_config.page_bbox

    @cached_property
    def ocr_available(self):
        if ids := self.pdf_config.ocr_identifiers:
            for identifiers in ids:
                if self.metadata_identifier.matches(identifiers):
                    return True
        return False

    @lru_cache
    def get_pages(self) -> list[PdfPage]:
        logger.debug("Extracting text from PDF")
        document = self.document

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

        # certain statements requsire garbage collection, so that duplicate objects
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
    def _remove_vertical_text(page: Page):
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
        for block in page.get_text("dict", flags=TEXTFLAGS_TEXT)["blocks"]:
            for line in block["lines"]:
                writing_direction = line["dir"]
                if writing_direction != (1, 0):
                    page.add_redact_annot(line["bbox"])
        page.apply_redactions(images=0)
        return page

    @staticmethod
    def apply_ocr(document: PdfDocument) -> PdfDocument:
        # pylint: disable=import-outside-toplevel
        try:
            from ocrmypdf import Verbosity, configure_logging, ocr
            from ocrmypdf.exceptions import PriorOcrFoundError, TaggedPDFError
        except ImportError:
            logger.warning("ocrmypdf not installed, skipping OCR")
            return document

        added_ocr = False
        try:
            logger.debug(f"Attempting to apply OCR on {document.name}")
            original_metadata = document.metadata
            output_bytes = BytesIO()
            configure_logging(Verbosity.quiet)
            logging.getLogger("ocrmypdf").setLevel(logging.ERROR)
            ocr(
                BytesIO(document.tobytes()),
                output_bytes,
                language="eng",
                tesseract_config="tesseract.cfg",
                progress_bar=False,
                optimize=0,
                fast_web_view=999999,
                output_type="pdf",
            )
            output_bytes.seek(0)
            added_ocr = True
            if added_ocr:
                logger.debug(f"OCR applied to {document.name}")

        except (PriorOcrFoundError, TaggedPDFError) as err:
            logger.debug("OCR skipped: %s", str(err))

        # pylint: disable=attribute-defined-outside-init
        if added_ocr:
            logger.debug("Adding OCR layer to document")
            document = PdfDocument(file_bytes=output_bytes)
            document.metadata = original_metadata
        return document
