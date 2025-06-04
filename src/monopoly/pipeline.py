import csv
import logging
import re
from pathlib import Path

from dateparser import parse
from pydantic import SecretStr

from monopoly.config import DateOrder
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
        transaction_date_order = statement.config.transaction_date_order

        def convert_date(transaction: Transaction, transaction_date_order: DateOrder):
            """
            Convert each date to a ISO 8601 (YYYY-MM-DD) format.

            Implements cross-year logic by attributing transactions from
            October, November, and December to the previous year if
            the statement month is January.
            e.g. if the statement month is Jan/Feb 2024, transactions from
            Oct/Nov/Dec should be attributed to the previous year.
            """
            # do not include year if transaction already includes date
            has_year = bool(re.search(DateFormats.YYYY, transaction.date))

            if not has_year:
                transaction.date = f"{transaction.date} {statement_date.year}"

            parsed_date = parse(transaction.date, settings=transaction_date_order.settings)

            if not parsed_date:
                msg = "Could not convert date"
                raise RuntimeError(msg)

            if statement_date.month in START_OF_YEAR_MONTHS and parsed_date.month > YEAR_CUTOFF_MONTH and not has_year:
                parsed_date = parsed_date.replace(year=parsed_date.year - 1)

            return parsed_date.isoformat()[:10]

        logger.debug("Transforming dates to ISO 8601")

        for transaction in transactions:
            transaction.date = convert_date(transaction, transaction_date_order)
        return transactions

    @staticmethod
    def load(
        transactions: list[Transaction],
        statement: BaseStatement,
        output_directory: Path,
    ):
        if isinstance(output_directory, str):
            output_directory = Path(output_directory)

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
