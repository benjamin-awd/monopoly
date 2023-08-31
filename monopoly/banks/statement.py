import logging
import os
from dataclasses import dataclass
from datetime import datetime

from google.cloud import storage
from pandas import DataFrame

from monopoly.config import settings
from monopoly.constants import AMOUNT, DATE, ROOT_DIR
from monopoly.helpers import generate_name, upload_to_google_cloud_storage
from monopoly.pdf import PdfParser, StatementExtractor

logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
@dataclass
class BankStatement:
    account_name: str
    bank: str
    date_pattern: str
    pdf_file_path: str
    pdf_password: str
    transaction_pattern: str
    date_converter: callable = None
    pdf_page_range: tuple = (None, None)
    transform_dates: bool = True
    statement_date: datetime = None

    def extract(self):
        parser = PdfParser(self.pdf_file_path, self.pdf_password, self.pdf_page_range)
        pages = parser.get_pages()

        statement = StatementExtractor(
            self.transaction_pattern, self.date_pattern, pages
        )
        self.statement_date = statement.statement_date

        return statement.to_dataframe()

    def transform(self, df: DataFrame) -> DataFrame:
        logger.info("Running transformation functions on DataFrame")
        df[AMOUNT] = df[AMOUNT].astype(float)

        if self.transform_dates:
            df = self.transform_date_to_iso(df)

        return df

    def transform_date_to_iso(self, df: DataFrame) -> DataFrame:
        logger.info("Transforming dates from MM/DD")

        df[DATE] = df.apply(self.date_converter, axis=1)
        return df

    def _write_to_csv(self, df: DataFrame):
        filename = generate_name("file", self)

        file_path = os.path.join(ROOT_DIR, "output", filename)
        df.to_csv(file_path, index=False)

        return file_path

    def load(self, df: DataFrame, upload_to_cloud: bool = False):
        csv_file_path = self._write_to_csv(df)

        if upload_to_cloud:
            blob_name = generate_name("blob", self)
            upload_to_google_cloud_storage(
                client=storage.Client(),
                source_filename=csv_file_path,
                bucket_name=settings.gcs_bucket,
                blob_name=blob_name,
            )
            logger.info("Uploaded to %s", blob_name)
