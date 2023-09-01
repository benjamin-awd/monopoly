import logging
import os
from dataclasses import dataclass

from google.cloud import storage
from pandas import DataFrame

from monopoly.banks.statement import Statement
from monopoly.config import settings
from monopoly.constants import AMOUNT, DATE, ROOT_DIR
from monopoly.helpers import generate_name, upload_to_google_cloud_storage
from monopoly.pdf import PdfParser

logger = logging.getLogger(__name__)


@dataclass
class Pdf:
    file_path: str
    password: str
    page_range: tuple = (None, None)
    page_bbox: tuple = None


@dataclass
class Bank:
    account_name: str
    bank_name: str
    pdf: Pdf
    statement: Statement
    date_converter: callable = None
    transform_dates: bool = True

    def extract(self):
        parser = PdfParser(**self.pdf.__dict__)
        self.statement.pages = parser.get_pages()
        statement = Statement(**self.statement.__dict__)
        return statement.to_dataframe()

    def transform(self, df: DataFrame) -> DataFrame:
        logger.info("Running transformation functions on DataFrame")
        df[AMOUNT] = df[AMOUNT].astype(float)

        if self.transform_dates:
            df = self._transform_date_to_iso(df)

        return df

    def _transform_date_to_iso(self, df: DataFrame) -> DataFrame:
        logger.info("Transforming dates")

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
