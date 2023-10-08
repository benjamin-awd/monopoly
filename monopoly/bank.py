import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pandas import DataFrame

from monopoly.config import PdfConfig, StatementConfig, settings
from monopoly.constants import StatementFields
from monopoly.pdf import PdfParser
from monopoly.statement import Statement
from monopoly.storage import upload_to_cloud_storage, write_to_csv

logger = logging.getLogger(__name__)


@dataclass
class Bank:
    statement_config: StatementConfig
    file_path: str
    pdf_config: Optional[PdfConfig] = None
    transform_dates: bool = True

    def extract(self) -> Statement:
        parser = PdfParser(self.file_path, self.pdf_config)
        pages = parser.get_pages()
        statement = Statement(pages, self.statement_config)

        if not statement.transactions:
            raise ValueError("No transactions found - statement extraction failed")

        if not statement.statement_date:
            raise ValueError("No statement date found")

        return statement

    def transform(self, statement: Statement) -> DataFrame:
        logger.info("Running transformation functions on DataFrame")
        df = statement.df
        statement_date = statement.statement_date

        if self.transform_dates:
            df = self._transform_date_to_iso(df, statement_date)

        return df

    def _transform_date_to_iso(
        self, df: DataFrame, statement_date: datetime
    ) -> DataFrame:
        logger.info("Transforming dates to ISO 8601")
        df[StatementFields.DATE] = df.apply(
            self._convert_date, statement_date=statement_date, axis=1
        )
        return df

    def parse_date(self, date_str):
        date_format = self.statement_config.transaction_date_format
        parsed_date = datetime.strptime(date_str, date_format)
        return parsed_date.day, parsed_date.month

    def _convert_date(self, row, statement_date: datetime):
        row_day, row_month = self.parse_date(row[StatementFields.DATE])

        # Deal with mixed years from Jan/Dec
        if statement_date.month == 1 and row_month == 12:
            row_year = statement_date.year - 1
        else:
            row_year = statement_date.year

        return f"{row_year}-{row_month:02d}-{row_day:02d}"

    def load(
        self,
        df: DataFrame,
        statement: Statement,
        csv_file_path: str = None,
        upload_to_cloud: bool = False,
    ):
        csv_file_path = write_to_csv(
            df=df, csv_file_path=csv_file_path, statement=statement
        )

        if upload_to_cloud:
            upload_to_cloud_storage(
                statement=statement,
                source_filename=csv_file_path,
                bucket_name=settings.gcs_bucket,
            )
