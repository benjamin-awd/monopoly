import re
import pandas as pd

import pytesseract
import pikepdf
from pdf2image import convert_from_path
from monopoly.enums import BankStatement
import re
import tempfile


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
                        {
                            BankStatement.DATE.value: date,
                            BankStatement.DESCRIPTION.value: description,
                            BankStatement.AMOUNT.value: amount
                        })

        return extracted_data


    def extract(self, columns: list = [e.value for e in BankStatement]):
        extracted_data = self._extract_text_from_pdf()
        self.df = pd.DataFrame(extracted_data, columns=columns)
