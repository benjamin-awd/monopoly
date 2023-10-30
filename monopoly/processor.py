import logging
from datetime import datetime
from typing import Optional

from pandas import DataFrame

from monopoly.config import BruteForceConfig, StatementConfig
from monopoly.constants import StatementFields
from monopoly.pdf import PdfConfig, PdfParser
from monopoly.statement import Statement
from monopoly.storage import write_to_csv

logger = logging.getLogger(__name__)


class StatementProcessor(PdfParser):
    def __init__(
        self, statement_config, file_path, pdf_config=None, brute_force_config=None
    ):
        self.statement_config: StatementConfig = statement_config
        self.pdf_config: PdfConfig = pdf_config
        self.brute_force_config: BruteForceConfig = brute_force_config

        # provide access to get_pages()
        super().__init__(file_path, brute_force_config, pdf_config)

    def extract(self) -> Statement:
        pages = self.get_pages(self.brute_force_config)
        statement = Statement(pages, self.statement_config)

        if not statement.transactions:
            raise ValueError("No transactions found - statement extraction failed")

        if not statement.statement_date:
            raise ValueError("No statement date found")

        return statement

    def transform(self, statement: Statement) -> DataFrame:
        logger.info("Running transformation functions on DataFrame")
        df = self._transform_date_to_iso(statement.df, statement.statement_date)

        return df

    def _transform_date_to_iso(
        self, df: DataFrame, statement_date: datetime
    ) -> DataFrame:
        logger.info("Transforming dates to ISO 8601")
        df[StatementFields.TRANSACTION_DATE] = df.apply(
            self._convert_date, statement_date=statement_date, axis=1
        )
        return df

    def parse_date(self, date_str):
        date_format = self.statement_config.transaction_date_format
        parsed_date = datetime.strptime(date_str, date_format)
        return parsed_date.day, parsed_date.month

    def _convert_date(self, row, statement_date: datetime):
        row_day, row_month = self.parse_date(row[StatementFields.TRANSACTION_DATE])

        # Deal with mixed years from Jan/Dec
        if statement_date.month == 1 and row_month == 12:
            row_year = statement_date.year - 1
        else:
            row_year = statement_date.year

        return f"{row_year}-{row_month:02d}-{row_day:02d}"

    def load(
        self, df: DataFrame, statement: Statement, csv_file_path: Optional[str] = None
    ):
        csv_file_path = write_to_csv(
            df=df, csv_file_path=csv_file_path, statement=statement
        )

        return csv_file_path
