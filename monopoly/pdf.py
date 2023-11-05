import logging
import subprocess
from dataclasses import dataclass
from functools import cached_property
from io import BytesIO
from typing import Optional

import fitz
import pdftotext
from pdf2john import PdfHashExtractor

from monopoly.config import BruteForceConfig, PdfConfig

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
        file_path: str,
        brute_force_config: Optional[BruteForceConfig] = None,
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

        self.password = pdf_config.password
        self.page_range = slice(*pdf_config.page_range)
        self.page_bbox = pdf_config.page_bbox
        self.brute_force_config = brute_force_config

    def open(self, brute_force_config: Optional[BruteForceConfig] = None):
        """
        Opens and decrypts a PDF document
        """
        logger.info("Opening pdf from path %s", self.file_path)
        document = self.document

        if not document.is_encrypted:
            return document

        if self.password:
            document.authenticate(self.password)

            if document.is_encrypted:
                raise ValueError("Wrong password - unable to open document")

            return document

        # This attempts to unlock statements based on a common password,
        # followed by the last few digits of a card
        if brute_force_config:
            logger.info("Unlocking PDF using a string prefix with mask")
            password = self.unlock_pdf(
                static_string=brute_force_config.static_string,
                mask=brute_force_config.mask,
            )

            document.authenticate(password)

            if not document.is_encrypted:
                logger.debug("Successfully authenticated with password")
                return document

            # If no successful authentication, raise an error
            raise ValueError(
                "Unable to unlock PDF password using static string and mask"
            )

        if document.is_encrypted:
            raise RuntimeError("Document failed to open -- check password")

        raise RuntimeError("Failed to open document")

    def get_pages(self, brute_force_config=None) -> list[PdfPage]:
        logger.debug("Extracting text from PDF")
        document: fitz.Document = self.open(brute_force_config)

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
    def extractor(self) -> PdfHashExtractor:
        """
        Returns an instance of a PDF hash extractor, used
        to read encryption metadata and generate a password hash
        """
        return PdfHashExtractor(self.file_path)

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

    def unlock_pdf(self, static_string: Optional[str], mask: Optional[str]):
        """
        Extracts the hashed representation for a set of PDF passwords (owner/user),
        and attempts to automatically unlock/decrypt the PDF based on
        the static string and mask using `john`
        """
        hash_extractor = self.extractor
        pdf_hash = hash_extractor.parse()

        hash_path = ".hash"
        with open(hash_path, "w", encoding="utf-8") as file:
            file.write(pdf_hash)

        mask_command = [
            f"john --format=PDF --mask={static_string}{mask} {hash_path} --pot=.pot"
        ]
        process = subprocess.run(
            mask_command,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        if not process.returncode == 0:
            raise ValueError(f"Return code is not 0: {process}")

        show_command = ["john", "--show", hash_path, "--pot=.pot"]
        output = subprocess.run(
            show_command,
            text=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        if not output.returncode == 0:
            raise ValueError(f"Return code is not 0: {output}")

        if "1 password hash cracked, 0 left" not in output.stdout:
            raise ValueError(f"PDF was not unlocked: {output}")

        password = output.stdout.split("\n")[0].split(":")[-1]

        return password
