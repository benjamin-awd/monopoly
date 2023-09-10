import logging
import re
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property

from pandas import DataFrame

from monopoly.helpers.constants import AMOUNT, DATE, DESCRIPTION
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)


@dataclass
class StatementConfig:
    bank_name: str
    account_type: str
    statement_date_format: str
    transaction_pattern: str
    transaction_date_format: str
    date_pattern: str
    multiline_transactions: bool = False


@dataclass
class Statement:
    pages: list[PdfPage]
    columns = [DATE, DESCRIPTION, AMOUNT]
    config: StatementConfig

    @cached_property
    def transactions(self) -> list[dict]:
        transactions = []
        for page in self.pages:
            for i, line in enumerate(page.lines):
                item = self._process_line(line, page.lines, idx=i)
                transactions.append(item)

        return list(filter(None, transactions))

    def _process_line(self, line: str, page: list[str], idx: int) -> dict:
        if match := re.findall(self.config.transaction_pattern, line):
            date, description, amount = match[0]

            if self.config.multiline_transactions:
                try:
                    if not re.findall(self.config.transaction_pattern, page[idx + 1]):
                        description = " ".join([description, page[idx + 1]])
                except IndexError as err:
                    logger.debug(err)

            return {DATE: date, DESCRIPTION: description, AMOUNT: amount}
        return None

    @cached_property
    def statement_date(self):
        logger.info("Extracting statement date")
        first_page = self.pages[0]
        for line in first_page.lines:
            if match := re.findall(self.config.date_pattern, line):
                statement_date = match[0]
                logger.debug("Statement date found")
                return datetime.strptime(
                    statement_date, self.config.statement_date_format
                )
        return None

    @cached_property
    def df(self) -> DataFrame:
        return DataFrame(self.transactions, columns=self.columns)
