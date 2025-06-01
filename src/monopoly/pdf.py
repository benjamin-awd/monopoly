import logging
from dataclasses import dataclass
from functools import cached_property
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

import pdftotext
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymupdf import TEXTFLAGS_TEXT, Document, Page

from monopoly.identifiers import MetadataIdentifier

if TYPE_CHECKING:
    from monopoly.banks import BankBase

logger = logging.getLogger(__name__)

MIN_OCR_TEXT_LENGTH = 10


class MissingOCRError(Exception):
    """Error that is raised when PDF does not contain any selectable text."""


class PdfPasswords(BaseSettings):
    """
    Pydantic model that automatically populates variables from a .env file.

    Also populates using environment variable called `PDF_PASSWORDS`.
    e.g. export PDF_PASSWORDS='["password123", "secretpass"]'.
    """

    pdf_passwords: list[SecretStr] = [SecretStr("")]
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@dataclass
class PdfPage:
    """Contains the raw text of a PDF page, and allows access to the raw text."""

    raw_text: str

    @cached_property
    def lines(self) -> list[str]:
        return self.raw_text.split("\n")


class WrongPasswordError(Exception):
    """Exception raised when an incorrect password is provided."""


class MissingPasswordError(Exception):
    """Exception raised when the document is encrypted, but no password is provided."""


class BadPasswordFormatError(Exception):
    """Exception raised passwords are not provided in a proper format."""


class PdfDocument(Document):
    """Handles logic related to the opening, unlocking, and storage of a PDF document."""

    def __init__(
        self,
        file_path: Path | None = None,
        file_bytes: bytes | BytesIO | None = None,
        passwords: list[SecretStr] | None = None,
    ):
        self.file_path = file_path
        self.file_bytes = file_bytes
        self.passwords = passwords or PdfPasswords().pdf_passwords

        if not any([self.file_path, self.file_bytes]):
            msg = "Either `file_path` or `file_bytes` must be passed"
            raise RuntimeError(msg)

        if self.file_path and self.file_bytes:
            msg = "Only one of `file_path` or `file_bytes` should be passed"
            raise RuntimeError(msg)

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
            msg = "No password found in PDF configuration"
            raise MissingPasswordError(msg)

        if not any(str(password) for password in self.passwords):
            msg = "Password in PDF configuration is empty"
            raise MissingPasswordError(msg)

        if not isinstance(self.passwords, list):
            msg = "Passwords should be stored in a list"
            raise BadPasswordFormatError(msg)

        if not all(isinstance(item, SecretStr) for item in self.passwords):
            msg = "Passwords should be stored as SecretStr"
            raise BadPasswordFormatError(msg)

        for password in self.passwords:
            if self.authenticate(password.get_secret_value()):
                logger.debug("Successfully authenticated with password")
                return self

        msg = f"Could not open document: {self.name}"
        raise WrongPasswordError(msg)

    @cached_property
    def raw_text(self) -> str:
        """Extracts and returns the text from the PDF."""
        raw_text = ""
        for page in self:
            raw_text += page.get_text()
        return raw_text


class PdfParser:
    def __init__(
        self,
        bank: type["BankBase"],
        document: PdfDocument,
    ):
        """
        Class responsible for parsing PDFs and returning raw text.

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

    @cached_property
    def pages(self):
        return self._get_pages()

    def _get_pages(self) -> list[PdfPage]:
        logger.debug("Extracting text from PDF")
        document = self.document

        num_pages = list(range(document.page_count))
        document.select(num_pages[self.page_range])

        if cropbox := self.page_bbox:
            logger.debug("Will crop pages with crop box %s and remove vertical text", cropbox)

        pages = []
        for page in document:
            if self.page_bbox:
                page.set_cropbox(cropbox)
            pages.append(self._remove_vertical_text(page))

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
                if all(len(page) < MIN_OCR_TEXT_LENGTH for page in pdf):
                    msg = "No selectable text found"
                    raise MissingOCRError(msg)

                return [PdfPage(page) for page in pdf]
            except pdftotext.Error:
                continue
        msg = "Unable to retrieve pages"
        raise RuntimeError(msg)

    @staticmethod
    def _remove_vertical_text(page: Page):
        """
        Remove vertical text, based on writing direction (wdir).

        This helps avoid situations where the PDF is oddly parsed, due to vertical text
        inside the PDF.

        An example of vertical text breaking a transaction:
        ```
        'HEALTHY HARVEST CAFÉ SINGAPORE SG',
        'Co Reg No: 123456',
        '10 NOV 9.80',
        ```

        Note:
        ----
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
            logger.debug("Attempting to apply OCR on %s", document.name)
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
                logger.debug("OCR applied to %s", {document.name})

        except (PriorOcrFoundError, TaggedPDFError) as err:
            logger.debug("OCR skipped: %s", str(err))

        # pylint: disable=attribute-defined-outside-init
        if added_ocr:
            logger.debug("Adding OCR layer to document")
            document = PdfDocument(file_bytes=output_bytes)
            document.metadata = original_metadata
        return document
