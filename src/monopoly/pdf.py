import logging
from dataclasses import dataclass
from functools import cached_property
from io import BytesIO
from pathlib import Path
from typing import Optional

import fitz
import pdftotext
from pdf2john import PdfHashExtractor as EncryptionMetadataExtractor

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
        return list(filter(None, self.raw_text.split("\n")))


class PdfParser:
    def __init__(
        self,
        file_path: Path,
        pdf_config: Optional[PdfConfig] = None,
    ):
        """
        Class responsible for parsing PDFs and returning raw text

        The page_range variable determines which pages are extracted.
        All pages are extracted by default.
        """
        self.file_path = file_path

        if pdf_config is None:
            pdf_config = PdfConfig()

        self.passwords = pdf_config.passwords
        self.page_range = slice(*pdf_config.page_range)
        self.page_bbox = pdf_config.page_bbox

    def open(self):
        """
        Opens and decrypts a PDF document
        """
        logger.debug("Opening pdf from path %s", self.file_path)
        document = self.document

        if not document.is_encrypted:
            return document

        if self.passwords:
            for password in self.passwords:
                document.authenticate(password)

                if not document.is_encrypted:
                    logger.debug("Successfully authenticated with password")
                    return document

        raise ValueError(f"Wrong password - unable to open document {document}")

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

        pdf_byte_stream = BytesIO(document.tobytes())
        pdf = pdftotext.PDF(pdf_byte_stream, physical=True)

        return [PdfPage(page) for page in pdf]

    @cached_property
    def document(self) -> fitz.Document:
        """
        Returns a Python representation of a PDF document.
        """
        return fitz.Document(self.file_path)

    @cached_property
    def extractor(self) -> EncryptionMetadataExtractor:
        """
        Returns an instance of pdf2john, used to retrieve and return
        the encryption metadata from a PDF's encryption dictionary
        """
        return EncryptionMetadataExtractor(self.file_path)

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
