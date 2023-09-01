import logging

import fitz
import pytesseract
from PIL import Image

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
        self.page_bbox: tuple = None
        self.remove_vertical_text = True

    def open(self):
        logger.info("Opening pdf from path %s", self.file_path)
        document = fitz.Document(self.file_path)
        document.authenticate(self.password)

        if document.is_encrypted:
            raise ValueError("Wrong password - document is encrypted")
        return document

    def get_pages(self) -> list[str]:
        logger.info("Extracting text from PDF")
        document: fitz.Document = self.open()

        num_pages = list(range(document.page_count))
        document.select(num_pages[self.page_range])

        return [self._process_page(page) for page in document]

    def _process_page(self, page: fitz.Page) -> list[str]:
        if self.page_bbox:
            logger.debug("Cropping page")
            page.set_cropbox(self.page_bbox)

        if self.remove_vertical_text:
            logger.debug("Removing vertical text")
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
