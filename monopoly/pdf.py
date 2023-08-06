import re
import tempfile

import pandas as pd
import pikepdf
import pytesseract
from pdf2image import convert_from_path

from monopoly.constants import AMOUNT, DATE, DESCRIPTION


class PDF:
    def __init__(self, file_path: str, password: str = ""):
        self.file_path: str = file_path
        self.password: str = password
        self.regex_pattern: str
        self.file_name: str
        self.pages: list[list[str]]
        self.df: pd.DataFrame

    def _open_pdf(self):
        pdf = pikepdf.open(self.file_path, password=self.password)
        self.file_name = pdf.filename

        with tempfile.NamedTemporaryFile() as tmp:
            pdf.save(tmp.name)
            return convert_from_path(tmp.name)

    def _extract_text_from_pdf(self) -> list[list[str]]:
        doc = self._open_pdf()
        pages = []

        for _, page_data in enumerate(doc):
            text = pytesseract.image_to_string(page_data)
            lines = text.split("\n")
            pages.append(lines)

        return pages

    def _extract_transactions_from_text(self, pages) -> list[dict[str, str]]:
        transactions = []
        for page in pages:
            for line in page:
                match = re.match(self.regex_pattern, line)
                if match:
                    date, description, amount = match.groups()

                    transactions.append(
                        {DATE: date, DESCRIPTION: description, AMOUNT: amount}
                    )

            return transactions

    def extract(
        self, columns: list = [DATE, DESCRIPTION, AMOUNT]
    ) -> pd.DataFrame:
        self.pages = self._extract_text_from_pdf()
        transactions = self._extract_transactions_from_text(self.pages)

        return pd.DataFrame(transactions, columns=columns)
