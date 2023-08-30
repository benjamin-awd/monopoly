import logging
import re
from datetime import datetime

import fitz
import pytesseract
from pandas import DataFrame
from PIL import Image

from monopoly.constants import AMOUNT, DATE, DESCRIPTION

logger = logging.getLogger(__name__)


class PdfParser:
    def __init__(
        self, file_path: str, password: str = "", page_range: tuple = (None, None)
    ):
        """Class responsible for parsing PDFs and returning raw text

        The page_range variable determines which pages are extracted.
        All pages are extracted by default.
        """
        self.file_path = file_path
        self.password = password
        self.page_range = slice(*page_range)

    def open(self):
        logger.info("Opening pdf from path %s", self.file_path)
        document = fitz.Document(self.file_path)
        document.authenticate(self.password)

        if document.is_encrypted:
            raise ValueError("Wrong password - document is encrypted")
        return document

    def get_pages(self) -> list[fitz.Page]:
        logger.info("Extracting text from PDF")
        document: fitz.Document = self.open()

        num_pages = list(range(document.page_count))
        document.select(num_pages[self.page_range])

        return [self._process_page(page) for page in document]

    def _process_page(self, page: fitz.Page) -> list[str]:
        page = self._remove_vertical_text(page)
        logger.debug("Creating pixmap for page")
        pix = page.get_pixmap(dpi=300, colorspace=fitz.csGRAY)

        logger.debug("Converting pixmap to PIL image")
        image = Image.frombytes("L", [pix.width, pix.height], pix.samples)

        logger.debug("Extracting string from image")
        text = pytesseract.image_to_string(image, config="--psm 6")
        lines = text.split("\n")
        return lines

    @staticmethod
    def _remove_vertical_text(page: fitz.Page):
        """Helper function to remove vertical text, based on writing direction (wdir).

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


class StatementExtractor:
    def __init__(
        self, transaction_pattern: str, date_pattern: str, pages: list[fitz.Page]
    ):
        self.transaction_pattern = transaction_pattern
        self.date_pattern = date_pattern
        self.pages = pages
        self.columns = [DATE, DESCRIPTION, AMOUNT]

    @property
    def transactions(self):
        return self._process_transactions()

    @property
    def statement_date(self):
        return self._extract_statement_date()

    def to_dataframe(self):
        return DataFrame(self.transactions, columns=self.columns)

    def _process_transactions(self) -> list[dict[str, str]]:
        transactions = []
        for page in self.pages:
            for line in page:
                match = re.match(self.transaction_pattern, line)
                if match:
                    date, description, amount = match.groups()

                    transactions.append(
                        {DATE: date, DESCRIPTION: description, AMOUNT: amount}
                    )

        return transactions

    def _extract_statement_date(self) -> datetime:
        logger.info("Extracting statement date")
        first_page = self.pages[0]
        for line in first_page:
            if match := re.match(self.date_pattern, line):
                statement_date = match.group()
                logger.debug("Statement date found")
                return datetime.strptime(statement_date, "%d-%m-%Y")
        return None
