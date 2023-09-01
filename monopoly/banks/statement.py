import logging
import re
from dataclasses import dataclass
from datetime import datetime

import fitz
from pandas import DataFrame

from monopoly.constants import AMOUNT, DATE, DESCRIPTION

logger = logging.getLogger(__name__)


@dataclass
class Statement:
    transaction_pattern: str
    date_pattern: str
    multiline_transactions: bool = False
    pages: list[fitz.Page] = None
    columns = [DATE, DESCRIPTION, AMOUNT]

    @property
    def transactions(self) -> list[dict]:
        transactions = []
        for page in self.pages:
            for i, line in enumerate(page):
                item = self._process_line(line, page, idx=i)
                transactions.append(item)

        return list(filter(None, transactions))

    def _process_line(self, line: str, page: fitz.Page, idx: int) -> dict:
        if match := re.match(self.transaction_pattern, line):
            date, description, amount = match.groups()

            if self.multiline_transactions:
                if not re.match(self.transaction_pattern, page[idx + 1]):
                    description = " ".join([description, page[idx + 1]])

            return {DATE: date, DESCRIPTION: description, AMOUNT: amount}
        return None

    @property
    def statement_date(self):
        logger.info("Extracting statement date")
        first_page = self.pages[0]
        for line in first_page:
            if match := re.match(self.date_pattern, line):
                statement_date = match.group()
                logger.debug("Statement date found")
                return datetime.strptime(statement_date, "%d-%m-%Y")
        return None

    def to_dataframe(self):
        return DataFrame(self.transactions, columns=self.columns)
