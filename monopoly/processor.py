import logging
from datetime import datetime
from typing import Optional

from pandas import DataFrame

from monopoly.config import BruteForceConfig, StatementConfig
from monopoly.constants import StatementFields
from monopoly.csv import write_to_csv
from monopoly.pdf import PdfConfig, PdfParser
from monopoly.statement import Statement

logger = logging.getLogger(__name__)


# pylint: disable=too-many-arguments
class StatementProcessor(PdfParser):
    """
    Handles extract, transform and load (ETL) logic for bank statements

    Transactions are extracted from pages, before undergoing various
    transformations like converting various date formats into ISO 8601.
    Transformed statements are then written to a CSV file.

    Since the auto-detect function already creates a parser, this class
    allows for the parser to be reused and avoid re-opening the PDF.
    """

    def __init__(
        self,
        statement_config: StatementConfig,
        file_path: str,
        pdf_config: Optional[PdfConfig] = None,
        brute_force_config: Optional[BruteForceConfig] = None,
        parser: Optional[PdfParser] = None,
        safety_check_enabled: bool = True,
    ):
        self.statement_config = statement_config
        self.pdf_config = pdf_config
        self.brute_force_config = brute_force_config
        self.safety_check_enabled = safety_check_enabled

        if not parser:
            super().__init__(file_path, brute_force_config, pdf_config)

    def extract(self) -> Statement:
        """Extracts transactions from the statement, and performs
        a safety check to make sure that total transactions add up"""
        pages = self.get_pages(self.brute_force_config)
        statement = Statement(pages, self.statement_config)

        if not statement.transactions:
            raise ValueError("No transactions found - statement extraction failed")

        if not statement.statement_date:
            raise ValueError("No statement date found")

        if self.safety_check_enabled:
            result = self._perform_safety_check(statement)
            if not result:
                logger.warning(
                    "Unable to verify that all transactions have been extracted"
                )

        return statement

    def _perform_safety_check(self, statement: Statement):
        """Checks that the total sum of all transactions is present
        somewhere within the document.

        Text is re-extracted from the page, as some bank-specific bounding-box
        configurations (e.g. HSBC) may preclude the total from being extracted
        """
        decimal_numbers = set()
        for page in self.document:
            lines = page.get_textpage().extractText().split("\n")
            decimal_numbers.update(statement.get_decimal_numbers(lines))
        total_amount = round(statement.df[StatementFields.AMOUNT].sum(), 2)
        if total_amount not in decimal_numbers:
            return False
        return True

    def transform(self, statement: Statement) -> DataFrame:
        logger.debug("Running transformation functions on DataFrame")
        df = self._transform_date_to_iso(statement.df, statement.statement_date)

        return df

    def _transform_date_to_iso(
        self, df: DataFrame, statement_date: datetime
    ) -> DataFrame:
        logger.debug("Transforming dates to ISO 8601")
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
