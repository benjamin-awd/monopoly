import logging
import os
from dataclasses import dataclass
from datetime import datetime

from google.cloud import storage
from pandas import DataFrame

from monopoly.banks.statement import Statement, StatementConfig
from monopoly.config import settings
from monopoly.constants import AMOUNT, DATE, ROOT_DIR
from monopoly.helpers import generate_name, upload_to_google_cloud_storage
from monopoly.pdf import PdfConfig, PdfParser

logger = logging.getLogger(__name__)


@dataclass
class Bank:
    pdf_config: PdfConfig
    statement_config: StatementConfig
    file_path: str
    date_parser: callable = None
    transform_dates: bool = True

    def extract(self) -> Statement:
        parser = PdfParser(self.file_path, self.pdf_config)
        pages = parser.get_pages()
        statement = Statement(pages, self.statement_config)

        if not statement.transactions:
            raise ValueError("No transactions found - statement extraction failed")

        return statement

    def transform(self, statement: Statement) -> DataFrame:
        logger.info("Running transformation functions on DataFrame")
        df = statement.df
        statement_date = statement.statement_date

        df[AMOUNT] = df[AMOUNT].str.replace(",", "").astype(float)

        if self.transform_dates:
            df = self._transform_date_to_iso(df, statement_date)

        return df

    def _transform_date_to_iso(
        self, df: DataFrame, statement_date: datetime
    ) -> DataFrame:
        logger.info("Transforming dates to ISO 8601")
        df[DATE] = df.apply(self._convert_date, statement_date=statement_date, axis=1)
        return df

    def _convert_date(self, row, statement_date: datetime):
        row_day, row_month = self.date_parser(row)

        # Deal with mixed years from Jan/Dec
        if statement_date.month == 1 and row_month == 12:
            row_year = statement_date.year - 1
        else:
            row_year = statement_date.year

        return f"{row_year}-{row_month:02d}-{row_day:02d}"

    def _write_to_csv(self, df: DataFrame, statement_date: datetime):
        filename = generate_name("file", self.statement_config, statement_date)

        file_path = os.path.join(ROOT_DIR, "output", filename)
        df.to_csv(file_path, index=False)

        return file_path

    def load(
        self,
        transformed_df: DataFrame,
        statement: Statement,
        upload_to_cloud: bool = False,
    ):
        statement_date = statement.statement_date
        csv_file_path = self._write_to_csv(transformed_df, statement_date)

        if upload_to_cloud:
            blob_name = generate_name("blob", self.statement_config, statement_date)
            upload_to_google_cloud_storage(
                client=storage.Client(),
                source_filename=csv_file_path,
                bucket_name=settings.gcs_bucket,
                blob_name=blob_name,
            )
            logger.info("Uploaded to %s", blob_name)


class BankBase(Bank):
    """Helper class to handle initialization of common variables
    that are shared between bank classes"""

    def __init__(self, file_path: str, date_parser: callable):
        super().__init__(
            statement_config=self.statement_config,
            pdf_config=self.pdf_config,
            date_parser=date_parser,
            file_path=file_path,
        )
