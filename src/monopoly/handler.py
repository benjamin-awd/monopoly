import csv
import logging
from datetime import datetime
from pathlib import Path

from dateparser import parse

from monopoly.config import DateOrder
from monopoly.pdf import PdfParser
from monopoly.statements import CreditStatement, DebitStatement
from monopoly.statements.transaction import Transaction
from monopoly.write import generate_name

logger = logging.getLogger(__name__)


class StatementHandler:
    """
    Handles extract, transform and load (ETL) logic for bank statements

    Transactions are extracted from pages, before undergoing various
    transformations like converting various date formats into ISO 8601.
    Transformed statements are then written to a CSV file.
    """

    def __init__(
        self,
        file_path: Path,
    ):
        self.parser = PdfParser(file_path=file_path)
        self.statement = self.get_statement(self.parser)
        self.transactions = self.statement.transactions

    @staticmethod
    def get_statement(parser: PdfParser) -> CreditStatement | DebitStatement:
        bank = parser.bank
        debit_config, credit_config = bank.debit_config, bank.credit_config

        if debit_config:
            debit_statement = DebitStatement(parser, debit_config)
            if debit_statement.debit_header:
                return debit_statement

        # if it's not a debit statement, assume that it's a credit statement
        return CreditStatement(parser, credit_config)

    def extract(self) -> CreditStatement | DebitStatement:
        """Extracts transactions from the statement, and performs
        a safety check to make sure that total transactions add up"""
        if not self.statement.transactions:
            raise ValueError("No transactions found - statement extraction failed")

        if not self.statement.statement_date:
            raise ValueError("No statement date found")

        self.statement.perform_safety_check()

        return self.statement

    @staticmethod
    def transform(
        transactions: list[Transaction],
        statement_date: datetime,
        transaction_date_order: DateOrder,
    ) -> list[Transaction]:
        logger.debug("Running transformation functions on DataFrame")

        def convert_date(transaction: Transaction, transaction_date_order: DateOrder):
            """
            Converts each date to a ISO 8601 (YYYY-MM-DD) format.

            Implements cross-year logic by attributing transactions from
            October, November, and December to the previous year if
            the statement month is January.
            e.g. if the statement month is Jan/Feb 2024, transactions from
            Oct/Nov/Dec should be attributed to the previous year.
            """
            transaction.transaction_date += f" {statement_date.year}"
            parsed_date = parse(
                transaction.transaction_date,
                settings=transaction_date_order.settings,
            )
            if parsed_date:
                if statement_date.month in (1, 2) and parsed_date.month > 2:
                    parsed_date = parsed_date.replace(year=parsed_date.year - 1)

                return parsed_date.isoformat()[:10]
            raise RuntimeError("Could not convert date")

        logger.debug("Transforming dates to ISO 8601")

        for transaction in transactions:
            transaction.transaction_date = convert_date(
                transaction, transaction_date_order
            )
        return transactions

    def load(
        self,
        transactions: list[Transaction],
        statement: CreditStatement | DebitStatement,
        output_directory: Path,
    ):
        if isinstance(output_directory, str):
            output_directory = Path(output_directory)

        filename = generate_name(
            document=self.parser.document,
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
                            transaction.transaction_date,
                            transaction.description,
                            transaction.amount,
                        ]
                    )
                )

        return output_path
