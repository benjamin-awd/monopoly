import logging
from datetime import datetime
from pathlib import Path

from pandas import DataFrame

from monopoly.config import CreditStatementConfig, DebitStatementConfig
from monopoly.constants import StatementFields
from monopoly.pdf import PdfParser
from monopoly.statements import CreditStatement, DebitStatement
from monopoly.write import generate_name

logger = logging.getLogger(__name__)


class StatementProcessor:
    """
    Handles extract, transform and load (ETL) logic for bank statements

    Transactions are extracted from pages, before undergoing various
    transformations like converting various date formats into ISO 8601.
    Transformed statements are then written to a CSV file.
    """

    credit_config: CreditStatementConfig
    debit_config: DebitStatementConfig
    statement: CreditStatement | DebitStatement

    def __init__(
        self,
        file_path: Path,
        parser: PdfParser,
        statement: CreditStatement | DebitStatement,
    ):
        self.file_path = file_path
        self.parser = parser
        self.statement = statement

    def extract(self) -> CreditStatement | DebitStatement:
        """Extracts transactions from the statement, and performs
        a safety check to make sure that total transactions add up"""
        statement = self.statement

        if not statement.transactions:
            raise ValueError("No transactions found - statement extraction failed")

        if not statement.statement_date:
            raise ValueError("No statement date found")

        statement.perform_safety_check()

        return statement

    def transform(self, statement: CreditStatement | DebitStatement) -> DataFrame:
        logger.debug("Running transformation functions on DataFrame")

        df = statement.df
        statement_date = statement.statement_date
        date_format = statement.statement_config.transaction_date_format

        def convert_date(row):
            parsed_date = datetime.strptime(
                row[StatementFields.TRANSACTION_DATE], date_format
            )
            row_year = statement_date.year
            row_day, row_month = parsed_date.day, parsed_date.month

            if statement_date.month == 1 and row_month == 12:
                row_year = statement_date.year - 1

            return f"{row_year}-{row_month:02d}-{row_day:02d}"

        logger.debug("Transforming dates to ISO 8601")
        df[StatementFields.TRANSACTION_DATE] = df.apply(convert_date, axis=1)
        return df

    def load(
        self,
        df: DataFrame,
        statement: CreditStatement | DebitStatement,
        output_directory: Path,
    ):
        if isinstance(output_directory, str):
            output_directory = Path(output_directory)

        filename = generate_name(
            file_path=self.file_path,
            format_type="file",
            statement_config=statement.statement_config,
            statement_type=statement.statement_type,
            statement_date=statement.statement_date,
        )

        output_path = output_directory / filename
        logger.debug("Writing CSV to file path: %s", output_path)
        df.to_csv(output_path, index=False)

        return output_path
