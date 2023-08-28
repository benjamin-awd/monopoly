import dataclasses
import logging
import os
import re
from datetime import datetime

import fitz
import pytesseract
from google.cloud import storage
from pandas import DataFrame
from PIL import Image

from monopoly.config import settings
from monopoly.constants import AMOUNT, DATE, DESCRIPTION, ROOT_DIR
from monopoly.helpers import generate_name, upload_to_google_cloud_storage

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Statement:
    bank: str
    account_name: str
    date: datetime
    date_pattern: str
    transaction_pattern: str
    filename: str = "statement.csv"


class PDF:
    def __init__(self, file_path: str = "", password: str = ""):
        self.file_path: str = file_path
        self.password: str = password
        self.file_name: str
        self.pages: list[list[str]]
        self.df: DataFrame

        self.statement: Statement

    @staticmethod
    def open(file_path: str, password: str) -> fitz.Document:
        logger.info("Opening pdf from path %s", file_path)
        pdf = fitz.Document(file_path)
        pdf.authenticate(password)

        if pdf.is_encrypted:
            raise ValueError("Wrong password - document is encrypted")

        return pdf

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
        """Helper function to remove vertical text, based on the writing direction (wdir).

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

    def _extract_text_from_pdf(self) -> list[list[str]]:
        logger.info("Extracting text from PDF")
        pdf = self.open(self.file_path, self.password)

        pages = [self._process_page(page) for page in pdf]
        self.file_name = pdf.name
        return pages

    def _extract_transactions_from_text(self, pages) -> list[dict[str, str]]:
        transactions = []
        logger.info("Extracting transactions from text")
        for page in pages:
            for line in page:
                match = re.match(self.statement.transaction_pattern, line)
                if match:
                    date, description, amount = match.groups()

                    transactions.append(
                        {DATE: date, DESCRIPTION: description, AMOUNT: amount}
                    )

        return transactions

    def extract_df_from_pdf(self, columns: list = None) -> DataFrame:
        logger.info("Extracting DataFrame from pdf")
        if not columns:
            columns = [DATE, DESCRIPTION, AMOUNT]
        self.pages = self._extract_text_from_pdf()
        transactions = self._extract_transactions_from_text(self.pages)

        return DataFrame(transactions, columns=columns)

    @staticmethod
    def transform_amount_to_float(df: DataFrame):
        logger.debug("Transforming amount column to `float`")
        df[AMOUNT] = df[AMOUNT].astype(float)
        return df

    def _write_to_csv(self, df: DataFrame):
        self.statement.filename = generate_name("file", self.statement)

        file_path = os.path.join(ROOT_DIR, "output", self.statement.filename)
        df.to_csv(file_path, index=False)

        return file_path

    def load(self, df: DataFrame, upload_to_cloud: bool = False):
        csv_file_path = self._write_to_csv(df)

        if upload_to_cloud:
            blob_name = generate_name("blob", self.statement)
            upload_to_google_cloud_storage(
                client=storage.Client(),
                source_filename=csv_file_path,
                bucket_name=settings.gcs_bucket,
                blob_name=blob_name,
            )
            logger.info("Uploaded to %s", blob_name)
