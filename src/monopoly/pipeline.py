import csv
import logging
from pathlib import Path
from typing import Optional, Type

from dateparser import parse
from pydantic import SecretStr

from monopoly.bank_detector import BankDetector
from monopoly.banks import BankBase
from monopoly.config import DateOrder
from monopoly.generic import GenericStatementHandler
from monopoly.generic.generic_handler import GenericBank
from monopoly.handler import StatementHandler
from monopoly.pdf import PdfDocument, PdfParser
from monopoly.statements import BaseStatement
from monopoly.statements.transaction import Transaction
from monopoly.write import generate_name

logger = logging.getLogger(__name__)


class Pipeline:
    """Handles extract, transform and load (ETL) logic for bank statements"""

    def __init__(
        self,
        file_path: Optional[Path] = None,
        file_bytes: Optional[bytes] = None,
        passwords: Optional[list[SecretStr]] = None,
        bank: Optional[Type[BankBase]] = None,
    ):
        self.file_path = file_path
        self.file_bytes = file_bytes
        self.passwords = passwords

        if not any([self.file_path, self.file_bytes]):
            raise RuntimeError("Either `file_path` or `file_bytes` must be passed")

        if self.file_path and self.file_bytes:
            raise RuntimeError(
                "Only one of `file_path` or `file_bytes` should be passed"
            )

        document = PdfDocument(passwords, file_bytes=file_bytes, file_path=file_path)
        bank = bank or self.detect_bank(document)
        parser = PdfParser(bank, document)
        self.handler = self.create_handler(bank, parser)

    @staticmethod
    def create_handler(
        bank: Type[BankBase], parser: PdfParser
    ) -> GenericStatementHandler | StatementHandler:
        if issubclass(bank, GenericBank):
            logger.debug("Using generic statement handler")
            return GenericStatementHandler(parser)
        logger.debug("Using statement handler with bank: %s", bank.__name__)
        return StatementHandler(parser)

    @staticmethod
    def detect_bank(document) -> Type[BankBase]:
        analyzer = BankDetector(document)
        if bank := analyzer.detect_bank():
            return bank
        logger.warning("Unable to detect bank, transactions may be inaccurate")
        return GenericBank

    def extract(self, safety_check=True) -> BaseStatement:
        """Extracts transactions from the statement, and performs
        a safety check to make sure that total transactions add up"""
        statement = self.handler.statement
        transactions = statement.get_transactions()

        if not transactions:
            raise ValueError("No transactions found - statement extraction failed")

        logger.debug("%s transactions found", len(transactions))

        if not statement.statement_date:
            raise ValueError("No statement date found")

        if safety_check:
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
            transaction.date += f" {statement_date.year}"
            parsed_date = parse(
                transaction.date,
                settings=transaction_date_order.settings,
            )
            if parsed_date:
                if statement_date.month in (1, 2) and parsed_date.month > 2:
                    parsed_date = parsed_date.replace(year=parsed_date.year - 1)

                return parsed_date.isoformat()[:10]
            raise RuntimeError("Could not convert date")

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
            statement_config=statement.config,
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
