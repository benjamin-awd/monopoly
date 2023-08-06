import re
import pandas as pd

import pytesseract
import pikepdf
from pdf2image import convert_from_path
import re
import tempfile


class PDF:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.password: str
        self.regex_pattern: str
        self.file_name: str
        self.df: pd.DataFrame

    def extract(self):
        pdf = pikepdf.open(self.file_path, password=self.password)
        self.file_name = pdf.filename

        df = pd.DataFrame(columns=["Date", "Merchant Details", "Transaction Amount"])
        extracted_data = []

        with tempfile.NamedTemporaryFile() as tmp:
            pdf.save(tmp.name)
            doc = convert_from_path(tmp.name)

        for _, page_data in enumerate(doc):
            text = pytesseract.image_to_string(page_data)

            lines = text.split("\n")

            for line in lines:
                match = re.match(self.regex_pattern, line)
                if match:
                    date = match.group(1)
                    merchant_details = match.group(2)
                    transaction_amount = match.group(3)

                    extracted_data.append(
                        {
                            "Date": date,
                            "Merchant Details": merchant_details,
                            "Transaction Amount": transaction_amount
                        })

        self.df = pd.concat([df, pd.DataFrame(extracted_data)])
