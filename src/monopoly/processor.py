import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from pandas import DataFrame

from monopoly.config import (
    BruteForceConfig,
    PdfConfig,
    StatementConfig,
    TransactionConfig,
)
from monopoly.constants import StatementFields
from monopoly.pdf import PdfParser
from monopoly.statement import Statement
from monopoly.write import write_to_csv

logger = logging.getLogger(__name__)


class StatementProcessor(PdfParser):
    statement_config: StatementConfig
    transaction_config: TransactionConfig
    pdf_config: Optional[PdfConfig] = None
    brute_force_config: Optional[BruteForceConfig] = None
    parser: Optional[PdfParser] = None
    safety_check_enabled: bool = True

    """
    Handles extract, transform and load (ETL) logic for bank statements

    Transactions are extracted from pages, before undergoing various
    transformations like converting various date formats into ISO 8601.
    Transformed statements are then written to a CSV file.

    Since the auto-detect function already creates a parser, this class
    allows for the parser to be reused and avoid re-opening the PDF.
    """

    def __init__(self, file_path: Path, parser: Optional[PdfParser] = None, **kwargs):
        keys = [
            "statement_config",
            "transaction_config",
            "pdf_config",
            "brute_force_config",
            "safety_check_enabled",
        ]

        for key, value in kwargs.items():
            if key in keys:
                setattr(self, key, value)

        if not parser:
            super().__init__(file_path, self.brute_force_config, self.pdf_config)

    def extract(self) -> Statement:
        """Extracts transactions from the statement, and performs
        a safety check to make sure that total transactions add up"""
        pages = self.get_pages(self.brute_force_config)
        statement = Statement(pages, self.statement_config, self.transaction_config)

        if not statement.transactions:
            raise ValueError("No transactions found - statement extraction failed")

        if not statement.statement_date:
            raise ValueError("No statement date found")

        if self.safety_check_enabled:
            self._perform_safety_check(statement)

        return statement

    def _perform_safety_check(self, statement: Statement) -> bool:
        """Checks that the total sum of all transactions is present
        somewhere within the document

        Text is re-extracted from the page, as some bank-specific bounding-box
        configurations (e.g. HSBC) may preclude the total from being extracted

        Returns `False` if the total does not exist in the document.
        """
        decimal_numbers = set()
        for page in self.document:
            lines = page.get_textpage().extractText().split("\n")
            decimal_numbers.update(statement.get_decimal_numbers(lines))
        total_amount = round(statement.df[StatementFields.AMOUNT].sum(), 2)

        result = total_amount in decimal_numbers
        if not result:
            logger.warning(
                "Total amount %s cannot be found in document - %s",
                total_amount,
                "transactions may be missing or inaccurate",
            )
        return result

    def transform(self, statement: Statement) -> DataFrame:
        logger.debug("Running transformation functions on DataFrame")

        df = statement.df
        statement_date = statement.statement_date
        date_format = self.transaction_config.date_format

        def convert_date(row):
            parsed_date = datetime.strptime(
                row[StatementFields.TRANSACTION_DATE], date_format
            )
            row_day, row_month = parsed_date.day, parsed_date.month

            if statement_date.month == 1 and row_month == 12:
                row_year = statement_date.year - 1
            else:
                row_year = statement_date.year

            return f"{row_year}-{row_month:02d}-{row_day:02d}"

        logger.debug("Transforming dates to ISO 8601")
        df[StatementFields.TRANSACTION_DATE] = df.apply(convert_date, axis=1)
        return df

    def load(
        self, df: DataFrame, statement: Statement, csv_file_path: Optional[str] = None
    ):
        csv_file_path = write_to_csv(
            df=df, csv_file_path=csv_file_path, statement=statement
        )

        return csv_file_path
