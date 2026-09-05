import csv
import json
import logging
import re
from datetime import datetime
from functools import cached_property
from pathlib import Path

from pydantic import SecretStr

from monopoly.constants.date import DateFormats
from monopoly.generic import GenericBank, GenericStatementHandler
from monopoly.handler import StatementHandler
from monopoly.pdf import PdfParser
from monopoly.serialize import statement_to_dict
from monopoly.statements import BaseStatement, NoTransactionsFoundError, Transaction
from monopoly.write import generate_name

logger = logging.getLogger(__name__)

START_OF_YEAR_MONTHS = (1, 2)
YEAR_CUTOFF_MONTH = 2
_YYYY_RE = re.compile(DateFormats.YYYY)


class Pipeline:
    """Handles extract, transform and load (ETL) logic for bank statements."""

    def __init__(
        self,
        parser: PdfParser,
        passwords: list[SecretStr] | None = None,
    ):
        self.parser = parser
        self.passwords = passwords

    @cached_property
    def handler(self) -> StatementHandler:
        # Constructed lazily so tier-1 failures (which can occur during handler
        # construction, e.g. GenericParserError) surface inside extract() rather
        # than in __init__ — a prerequisite for the extraction cascade.
        return self.create_handler(self.parser)

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
            raise NoTransactionsFoundError(msg)

        logger.debug("%s transactions found", len(statement.transactions))

        if not statement.statement_date:
            msg = "No statement date found"
            raise ValueError(msg)

        if safety_check and statement.config.safety_check:
            statement.perform_safety_check()

        # Stamp the statement's settlement currency onto every transaction. Read
        # from the matched `StatementConfig` (not the bank class) so multi-country
        # banks resolve correctly — the handler has already selected the one config
        # for this statement. Done here rather than in the static `transform`
        # because `extract` runs before `transform` in every real pipeline path.
        # Configs with no known currency (generic handler, unset) leave it None.
        if currency := statement.config.currency:
            for tx in statement.transactions:
                tx.currency = currency

        return statement

    @staticmethod
    def transform(statement: BaseStatement) -> list[Transaction]:
        logger.debug("Running transformation functions on DataFrame")

        transactions = statement.transactions
        statement_date = statement.statement_date
        date_order = statement.config.transaction_date_order
        date_format = statement.config.transaction_date_format

        def convert_date(date_str: str) -> str:
            """
            Convert a date string to ISO 8601 format with cross-year logic.

            Applies the following logic:
            - If the date does not include a year, append the year from the statement date.
            - Attempts to parse the date using a specified format (for performance).
            - Falls back to a flexible date parser if format-based parsing fails.
            - Applies cross-year adjustment: if the statement is from early in the year and
            the date appears to be from a late-month (e.g., December), it may belong
            to the previous year and is adjusted accordingly.
            """
            has_year = bool(_YYYY_RE.search(date_str))
            needs_year = not has_year and "y" not in date_format.lower()
            fmt = date_format
            parsed_date = None

            if needs_year:
                date_str = f"{date_str} {statement_date.year}"
                fmt += " %Y"

            try:
                parsed_date = datetime.strptime(date_str, fmt).astimezone()
            except ValueError:
                logger.debug("strptime failed for %s with format %s", date_str, fmt)
                from dateparser import parse

                parsed_date = parse(date_str, settings=date_order.settings)

            if not parsed_date:
                msg = f"Could not convert date: {date_str}"
                raise RuntimeError(msg)

            # Detect cross-year case: e.g., statement is from Jan/Feb, but tx is Dec
            is_cross_year = statement_date.month in START_OF_YEAR_MONTHS and parsed_date.month > YEAR_CUTOFF_MONTH

            if is_cross_year and needs_year:
                parsed_date = parsed_date.replace(year=parsed_date.year - 1)

            return parsed_date.date().isoformat()

        logger.debug("Transforming dates to ISO 8601")

        for tx in transactions:
            tx.date = convert_date(tx.date)
            # posting_date shares the transaction date format; normalize it too so
            # both dates in the JSON output are ISO 8601.
            if tx.posting_date:
                tx.posting_date = convert_date(tx.posting_date)

        return transactions

    @staticmethod
    def load(
        transactions: list[Transaction],
        statement: BaseStatement,
        output_directory: Path | str,
        *,
        preserve_filename: bool,
        format_type: str = "csv",
    ):
        # guard direct library callers; the CLI already restricts this via click.Choice
        if format_type not in ("csv", "json"):
            msg = f"Unsupported output format: {format_type!r} (expected 'csv' or 'json')"
            raise ValueError(msg)

        output_directory = Path(output_directory)

        if preserve_filename and statement.file_path:
            stem = Path(statement.file_path).stem
        else:
            stem = Path(
                generate_name(
                    statement=statement,
                    format_type="file",
                    bank_name=statement.bank_name,
                    statement_type=statement.statement_type,
                    statement_date=statement.statement_date,
                )
            ).stem

        # generate_name (and the preserve branch) yield a .csv stem; the extension
        # follows the requested output format.
        output_path = output_directory / f"{stem}.{format_type}"
        logger.debug("Writing %s to file path: %s", format_type, output_path)

        if format_type == "json":
            Pipeline._write_json(output_path, statement, transactions)
        else:
            Pipeline._write_csv(output_path, statement, transactions)

        return output_path

    @staticmethod
    def _write_csv(output_path: Path, statement: BaseStatement, transactions: list[Transaction]) -> None:
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
                        transaction.balance or 0,
                    ]
                )

    @staticmethod
    def _write_json(output_path: Path, statement: BaseStatement, transactions: list[Transaction]) -> None:
        with open(output_path, mode="w", encoding="utf8") as file:
            json.dump(statement_to_dict(statement, transactions), file, indent=2)
