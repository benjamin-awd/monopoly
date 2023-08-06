import re
import tempfile

import pandas as pd
import pikepdf
import pytesseract
from pdf2image import convert_from_path

from monopoly.constants import AMOUNT, DATE, DESCRIPTION


class PDF:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.password: str
        self.regex_pattern: str
        self.file_name: str
        self.df: pd.DataFrame

    def _extract_text_from_pdf(self):
        pdf = pikepdf.open(self.file_path, password=self.password)
        self.file_name = pdf.filename

        with tempfile.NamedTemporaryFile() as tmp:
            pdf.save(tmp.name)
            doc = convert_from_path(tmp.name)

        extracted_data = []

        for _, page_data in enumerate(doc):
            text = pytesseract.image_to_string(page_data)

            lines = text.split("\n")

            for line in lines:
                match = re.match(self.regex_pattern, line)
                if match:
                    date, description, amount = match.groups()

                    extracted_data.append(
                        {DATE: date, DESCRIPTION: description, AMOUNT: amount}
                    )

        return extracted_data

    def extract(self, columns: list = [DATE, DESCRIPTION, AMOUNT]):
        extracted_data = self._extract_text_from_pdf()
        self.df = pd.DataFrame(extracted_data, columns=columns)
