import csv
import logging
import re
from datetime import datetime
from pathlib import Path

from pydantic import SecretStr

from monopoly.constants.date import DateFormats
from monopoly.generic import GenericBank, GenericStatementHandler
from monopoly.handler import StatementHandler
from monopoly.pdf import PdfParser
from monopoly.statements import BaseStatement, Transaction
from monopoly.write import generate_name

logger = logging.getLogger(__name__)

START_OF_YEAR_MONTHS = (1, 2)
YEAR_CUTOFF_MONTH = 2


class Pipeline:
    """Handles extract, transform and load (ETL) logic for bank statements."""

    def __init__(
        self,
        parser: PdfParser,
        passwords: list[SecretStr] | None = None,
    ):
        self.passwords = passwords
        self.handler = self.create_handler(parser)

    @staticmethod
    def create_handler(parser: PdfParser) -> StatementHandler:
        if issubclass(parser.bank, GenericBank):
            logger.debug("Using generic statement handler")
            return GenericStatementHandler(parser)
        logger.debug("Using statement handler with bank: %s", parser.bank.__name__)
        return StatementHandler(parser)

    def extract(self, *_, safety_check=True) -> BaseStatement:
        """
        Extract transactions from the statement.

        Perform a safety check to make sure that total transactions add up.
        """
        statement = self.handler.statement

        if not statement.transactions:
            msg = "No transactions found - statement extraction failed"
            raise ValueError(msg)

        logger.debug("%s transactions found", len(statement.transactions))

        if not statement.statement_date:
            msg = "No statement date found"
            raise ValueError(msg)

        if safety_check and statement.config.safety_check:
            statement.perform_safety_check()

        return statement

    @staticmethod
    def transform(statement: BaseStatement) -> list[Transaction]:
        logger.debug("Running transformation functions on DataFrame")

        transactions = statement.transactions
        statement_date = statement.statement_date
        date_order = statement.config.transaction_date_order
        date_format = statement.config.transaction_date_format

        def convert_date(tx: Transaction) -> str:
            """
            Convert date to ISO 8601 format with cross-year logic.

            Applies the following logic:
            - If the transaction date does not include a year, append the year from the statement date.
            - Attempts to parse the date using a specified format (for performance).
            - Falls back to a flexible date parser if format-based parsing fails.
            - Applies cross-year adjustment: if the statement is from early in the year and
            the transaction appears to be from a late-month (e.g., December), it may belong
            to the previous year and is adjusted accordingly.
            """
            has_year = bool(re.search(DateFormats.YYYY, tx.date))
            needs_year = not has_year and "y" not in date_format.lower()
            fmt = date_format
            parsed_date = None

            if needs_year:
                tx.date = f"{tx.date} {statement_date.year}"
                fmt += " %Y"

            try:
                parsed_date = datetime.strptime(tx.date, fmt).astimezone()
            except ValueError:
                logger.debug("strptime failed for %s with format %s", tx.date, fmt)
                from dateparser import parse

                parsed_date = parse(tx.date, settings=date_order.settings)

            if not parsed_date:
                msg = f"Could not convert date: {tx.date}"
                raise RuntimeError(msg)

            # Detect cross-year case: e.g., statement is from Jan/Feb, but tx is Dec
            is_cross_year = statement_date.month in START_OF_YEAR_MONTHS and parsed_date.month > YEAR_CUTOFF_MONTH

            if is_cross_year and needs_year:
                parsed_date = parsed_date.replace(year=parsed_date.year - 1)

            return parsed_date.date().isoformat()

        logger.debug("Transforming dates to ISO 8601")

        for tx in transactions:
            tx.date = convert_date(tx)

        return transactions

    @staticmethod
    def load(
        transactions: list[Transaction],
        statement: BaseStatement,
        output_directory: Path | str,
        *,
        preserve_filename: bool,
    ):
        output_directory = Path(output_directory)

        if preserve_filename and statement.file_path:
            filename = f"{Path(statement.file_path).stem}.csv"
        else:
            filename = generate_name(
                statement=statement,
                format_type="file",
                bank_name=statement.bank_name,
                statement_type=statement.statement_type,
                statement_date=statement.statement_date,
            )

        output_path = output_directory / filename
        logger.debug("Writing CSV to file path: %s", output_path)

        with open(output_path, mode="w", encoding="utf8") as file:
            writer = csv.writer(file)

            # header
            writer.writerow(statement.columns)

            for transaction in transactions:
                writer.writerow(
                    [
                        transaction.date,
                        transaction.description,
                        transaction.amount,
                    ]
                )

        return output_path
