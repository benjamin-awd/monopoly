import csv
import logging
import re
from pathlib import Path
from typing import Optional, Type

from dateparser import parse
from pydantic import SecretStr

from monopoly.banks import BankBase
from monopoly.config import DateOrder
from monopoly.constants.date import DateFormats
from monopoly.generic import GenericBank, GenericStatementHandler
from monopoly.handler import StatementHandler
from monopoly.pdf import PdfPage, PdfParser
from monopoly.statements import BaseStatement, Transaction
from monopoly.write import generate_name

logger = logging.getLogger(__name__)


class Pipeline:
    """Handles extract, transform and load (ETL) logic for bank statements"""

    def __init__(
        self,
        parser: PdfParser,
        passwords: Optional[list[SecretStr]] = None,
    ):
        self.passwords = passwords
        pages = parser.get_pages()
        self.handler = self.create_handler(parser.bank, pages)

    @staticmethod
    def create_handler(bank: Type[BankBase], pages: list[PdfPage]) -> StatementHandler:
        if issubclass(bank, GenericBank):
            logger.debug("Using generic statement handler")
            return GenericStatementHandler(bank, pages)
        logger.debug("Using statement handler with bank: %s", bank.__name__)
        return StatementHandler(bank, pages)

    def extract(self, safety_check=True) -> BaseStatement:
        """Extracts transactions from the statement, and performs
        a safety check to make sure that total transactions add up"""
        statement = self.handler.get_statement()
        transactions = statement.get_transactions()

        if not transactions:
            raise ValueError("No transactions found - statement extraction failed")

        logger.debug("%s transactions found", len(transactions))

        if not statement.statement_date:
            raise ValueError("No statement date found")

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
            Converts each date to a ISO 8601 (YYYY-MM-DD) format.

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

            parsed_date = parse(
                transaction.date, settings=transaction_date_order.settings
            )

            if not parsed_date:
                raise RuntimeError("Could not convert date")

            if (
                statement_date.month in (1, 2)
                and parsed_date.month > 2
                and not has_year
            ):
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
                    (
                        [
                            transaction.date,
                            transaction.description,
                            transaction.amount,
                        ]
                    )
                )

        return output_path
