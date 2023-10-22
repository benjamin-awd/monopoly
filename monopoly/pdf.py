import logging
import subprocess
from dataclasses import dataclass

import fitz
import pytesseract
from pdf2john import PdfHashExtractor
from PIL import Image

from monopoly.config import BruteForceConfig, PdfConfig

logger = logging.getLogger(__name__)


@dataclass
class PdfPage:
    pix_map: fitz.Pixmap
    raw_text: str
    image: object

    @property
    def lines(self) -> list:
        return list(filter(None, self.raw_text.split("\n")))


class PdfParser:
    def __init__(
        self,
        file_path: str,
        brute_force_config: BruteForceConfig = None,
        pdf_config: PdfConfig = None,
    ):
        """Class responsible for parsing PDFs and returning raw text

        The page_range variable determines which pages are extracted.
        All pages are extracted by default.
        """
        self.file_path = file_path

        if pdf_config is None:
            pdf_config = PdfConfig()

        self.password = pdf_config.password
        self.page_range = slice(*pdf_config.page_range)
        self.page_bbox: tuple = pdf_config.page_bbox
        self.psm: int = pdf_config.psm
        self.brute_force_config = brute_force_config
        self.remove_vertical_text = True

    def open(self, brute_force_config: BruteForceConfig = None):
        """
        Opens and decrypts a PDF document
        """
        logger.info("Opening pdf from path %s", self.file_path)
        document = fitz.Document(self.file_path)

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
                pdf_file_path=self.file_path,
                static_string=brute_force_config.static_string,
                mask=brute_force_config.mask,
            )

            document.authenticate(password)

            if not document.is_encrypted:
                logger.info("Successfully authenticated with password")
                return document

            # If no successful authentication, raise an error
            raise ValueError(
                "Unable to unlock PDF password using static string and mask"
            )

        return None

    def get_pages(self, brute_force_config=None) -> list[PdfPage]:
        logger.info("Extracting text from PDF")
        document: fitz.Document = self.open(brute_force_config)

        num_pages = list(range(document.page_count))
        document.select(num_pages[self.page_range])

        return [self._process_page(page) for page in document]

    @staticmethod
    def unlock_pdf(pdf_file_path: str, static_string: str, mask: str):
        hash_extractor = PdfHashExtractor(pdf_file_path)
        pdf_hash = hash_extractor.parse()

        hash_path = ".hash"
        with open(hash_path, "w", encoding="utf-8") as file:
            file.write(pdf_hash)

        mask_command = [
            f"john --format=PDF --mask={static_string}{mask} {hash_path} --pot=.pot"
        ]
        process = subprocess.run(mask_command, shell=True, check=False)

        if not process.returncode == 0:
            raise ValueError(f"Return code is not 0: {process}")

        show_command = ["john", "--show", hash_path, "--pot=.pot"]
        output = subprocess.run(
            show_command, capture_output=True, text=True, check=False
        )

        if not output.returncode == 0:
            raise ValueError(f"Return code is not 0: {output}")

        if "1 password hash cracked, 0 left" not in output.stdout:
            raise ValueError(f"PDF was not unlocked: {output}")

        password = output.stdout.split("\n")[0].split(":")[-1]

        return password

    def _process_page(self, page: fitz.Page) -> PdfPage:
        logger.info("Processing: %s", page)
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
        text = pytesseract.image_to_string(image, config=f"--psm {self.psm}")

        return PdfPage(pix_map=pix, raw_text=text, image=image)

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
