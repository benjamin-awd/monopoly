import logging
import os
import re
from datetime import datetime

from google.cloud import storage
from pandas import DataFrame

from monopoly.config import settings
from monopoly.constants import AMOUNT, DATE, ROOT_DIR
from monopoly.exceptions import UndefinedFilePathError
from monopoly.helpers import generate_name, upload_to_google_cloud_storage
from monopoly.pdf import PDF, Statement

logger = logging.getLogger(__name__)


class OCBC(PDF):
    def __init__(self, file_path: str = "", password: str = ""):
        super().__init__(file_path)

        self.password: str = password
        self.statement = Statement(
            bank="OCBC",
            account_name="365",
            date_pattern=r"\d{2}\-\d{2}\-\d{4}",
            date=None,
            transaction_pattern=r"(\d+\/\d+)\s*(.*?)\s*([\d.,]+)$",
        )

    def extract(self) -> DataFrame:
        if not self.file_path:
            raise UndefinedFilePathError("File path must be defined")

        df = super().extract_df_from_pdf()
        self.statement.date = self._extract_statement_date()
        return df

    def _extract_statement_date(self) -> datetime:
        logger.info("Extracting statement date")
        first_page = self.pages[0]
        for line in first_page:
            if match := re.match(self.statement.date_pattern, line):
                statement_date = match.group()
                logger.debug("Statement date found")
                return datetime.strptime(statement_date, "%d-%m-%Y")
        return None

    def transform(self, df: DataFrame) -> DataFrame:
        logger.info("Running transformation functions on DataFrame")
        df[AMOUNT] = df[AMOUNT].astype(float)
        df = self._transform_dates(df, self.statement.date)
        return df

    @staticmethod
    def _transform_dates(df: DataFrame, statement_date: datetime) -> DataFrame:
        logger.info("Transforming dates from MM/DD")

        def convert_date(row):
            row_day, row_month = map(int, row[DATE].split("/"))

            # Deal with mixed years from Jan/Dec
            if statement_date.month == 1 and row_month == 12:
                row_year = statement_date.year - 1
            else:
                row_year = statement_date.year

            return f"{row_year}-{row_month:02d}-{row_day:02d}"

        df[DATE] = df.apply(convert_date, axis=1)
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
