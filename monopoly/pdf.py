import os
import re
import tempfile
from datetime import datetime

import pikepdf
import pytesseract
from google.cloud import storage
from pandas import DataFrame
from pdf2image import convert_from_path

from monopoly.constants import AMOUNT, DATE, DESCRIPTION, ROOT_DIR
from monopoly.helpers import generate_name, upload_to_google_cloud_storage


class PDF:
    def __init__(self, file_path: str = "", password: str = ""):
        self.file_path: str = file_path
        self.password: str = password
        self.regex_pattern: str
        self.file_name: str
        self.pages: list[list[str]]
        self.df: DataFrame

        # The following uses credentials inferred from the local environment
        # using Application Default Credentials.
        # https://googleapis.dev/python/google-api-core/latest/auth.html
        self.storage_client = storage.Client()

        self.filename: str = "statement.csv"
        self.bank: str
        self.account_name: str
        self.statement_date: datetime

        self.gcs_bucket: str

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

    def extract_df_from_pdf(self, columns: list = None) -> DataFrame:
        if not columns:
            columns = [DATE, DESCRIPTION, AMOUNT]
        self.pages = self._extract_text_from_pdf()
        transactions = self._extract_transactions_from_text(self.pages)

        return DataFrame(transactions, columns=columns)

    @staticmethod
    def transform_amount_to_float(df: DataFrame):
        df[AMOUNT] = df[AMOUNT].astype(float)
        return df

    def _write_to_csv(self, df: DataFrame):
        self.filename = generate_name("file", self)

        file_path = os.path.join(ROOT_DIR, "output", self.filename)
        df.to_csv(file_path, index=False)

        return file_path

    def load(self, df: DataFrame, upload_to_cloud: bool = False):
        csv_file_path = self._write_to_csv(df)

        if upload_to_cloud:
            self.gcs_bucket = os.getenv("GCS_BUCKET")
            blob_name = generate_name("blob", self)
            upload_to_google_cloud_storage(
                client=self.storage_client,
                source_filename=csv_file_path,
                bucket_name=self.gcs_bucket,
                blob_name=blob_name,
            )
