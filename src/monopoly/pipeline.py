import csv
import logging
from pathlib import Path
from typing import Optional, Type

from dateparser import parse
from pydantic import SecretStr

from monopoly.banks import BankBase
from monopoly.config import DateOrder
from monopoly.generic import GenericStatementHandler
from monopoly.generic.generic_handler import GenericBank
from monopoly.handler import StatementHandler
from monopoly.metadata import MetadataAnalyzer
from monopoly.pdf import PdfParser
from monopoly.statements import CreditStatement, DebitStatement
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

        self.bank = self._detect_bank()
        self.parser = self._create_parser()
        self.handler = self._create_handler()
        self.statement = self.handler.get_statement(self.parser)

    def _create_parser(self) -> PdfParser:
        return PdfParser(
            self.bank,
            file_path=self.file_path,
            file_bytes=self.file_bytes,
            passwords=self.passwords,
        )

    def _create_handler(self) -> GenericStatementHandler | StatementHandler:
        if issubclass(self.bank, GenericBank):
            logger.debug("Using generic statement handler")
            return GenericStatementHandler(self.parser)
        logger.debug("Using statement handler with bank: %s", self.bank.__name__)
        return StatementHandler(self.parser)

    def _detect_bank(self) -> Type[BankBase]:
        analyzer = MetadataAnalyzer(
            file_path=self.file_path, file_bytes=self.file_bytes
        )
        if bank := analyzer.bank:
            return bank
        logger.warning("Unable to detect bank, transactions may be inaccurate")
        return GenericBank

    def extract(self, safety_check=True) -> CreditStatement | DebitStatement:
        """Extracts transactions from the statement, and performs
        a safety check to make sure that total transactions add up"""
        transactions = self.statement.transactions
        statement_date = self.statement.statement_date

        if not transactions:
            raise ValueError("No transactions found - statement extraction failed")

        logger.debug("%s transactions found", len(transactions))

        if not statement_date:
            raise ValueError("No statement date found")

        if safety_check:
            self.statement.perform_safety_check()

        return self.statement

    @staticmethod
    def transform(statement: CreditStatement | DebitStatement) -> list[Transaction]:
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
        statement: CreditStatement | DebitStatement,
        output_directory: Path,
    ):
        if isinstance(output_directory, str):
            output_directory = Path(output_directory)

        filename = generate_name(
            document=statement.document,
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
