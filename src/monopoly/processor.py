import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from pandas import DataFrame

from monopoly.config import CreditStatementConfig, DebitStatementConfig, PdfConfig
from monopoly.constants import AccountType, StatementFields
from monopoly.credit_statement import CreditStatement
from monopoly.debit_statement import DebitStatement
from monopoly.pdf import PdfPage, PdfParser
from monopoly.statement import Statement
from monopoly.write import generate_name

logger = logging.getLogger(__name__)


class StatementProcessor(PdfParser):
    credit_config: CreditStatementConfig
    debit_config: Optional[DebitStatementConfig]
    pdf_config: Optional[PdfConfig] = None
    parser: Optional[PdfParser] = None
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
            "credit_config",
            "debit_config",
            "pdf_config",
        ]

        for key, value in kwargs.items():
            if key in keys:
                setattr(self, key, value)

        if not parser:
            super().__init__(file_path, self.pdf_config)

    def extract(self) -> Statement:
        """Extracts transactions from the statement, and performs
        a safety check to make sure that total transactions add up"""
        pages = self.get_pages()
        account_type = self._get_account_type(pages)
        statement = self._get_statement(account_type, pages)

        if not statement.transactions:
            raise ValueError("No transactions found - statement extraction failed")

        if not statement.statement_date:
            raise ValueError("No statement date found")

        self._perform_safety_check(statement)

        return statement

    def _get_statement(
        self, account_type, pages: list[PdfPage]
    ) -> DebitStatement | CreditStatement:
        if account_type == AccountType.CREDIT:
            return CreditStatement(pages, self.credit_config)

        return DebitStatement(pages, self.debit_config)  # type: ignore

    def _get_account_type(self, pages: list[PdfPage]) -> str:
        config = self.debit_config
        if config and config.debit_account_identifier:
            for line in pages[0].lines:
                if re.search(config.debit_account_identifier, line):
                    return AccountType.DEBIT
        return AccountType.CREDIT

    def _perform_safety_check(self, statement: Statement) -> bool:
        """Checks that the total sum of all transactions is present
        somewhere within the document

        Text is re-extracted from the page, as some bank-specific bounding-box
        configurations (e.g. HSBC) may preclude the total from being extracted

        Returns `False` if the total does not exist in the document.
        """
        numbers = set()
        df = statement.df
        amount = StatementFields.AMOUNT
        warning_message = (
            "Safety check failed - transactions may be missing or inaccurate"
        )
        for page in self.document:
            lines = page.get_textpage().extractText().split("\n")
            numbers.update(statement.get_decimal_numbers(lines))

        total_amount = abs(round(df[amount].sum(), 2))

        if statement.account_type == AccountType.DEBIT:
            logger.debug(
                "Total amount %s cannot be found in document - %s",
                total_amount,
                "checking to see if debit/credit sum is present in document",
            )
            debit_sum = round(abs(df[df[amount] > 0][amount].sum()), 2)
            credit_sum = round(abs(df[df[amount] < 0][amount].sum()), 2)
            result = (debit_sum in numbers) == (credit_sum in numbers)
            if not result:
                logger.warning(warning_message)

        # handling for credit statement
        else:
            result = total_amount in numbers
            if not result:
                logger.warning(
                    "%s: total amount %s cannot be found in document",
                    warning_message,
                    total_amount,
                )
        return result

    def transform(self, statement: Statement) -> DataFrame:
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

    def load(self, df: DataFrame, statement: Statement, output_directory: Path):
        if isinstance(output_directory, str):
            output_directory = Path(output_directory)

        filename = generate_name(
            account_type=statement.account_type,
            file_path=self.file_path,
            format_type="file",
            config=statement.statement_config,
            statement_date=statement.statement_date,
        )

        output_path = output_directory / filename
        logger.debug("Writing CSV to file path: %s", output_path)
        df.to_csv(output_path, index=False)

        return output_path
