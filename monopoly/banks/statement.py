import logging
import re
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property

from pandas import DataFrame

from monopoly.constants import AMOUNT, DATE, DESCRIPTION
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)


@dataclass
class Statement:
    statement_date_format: str
    transaction_pattern: str
    date_pattern: str
    multiline_transactions: bool = False
    pages: list[PdfPage] = None
    columns = [DATE, DESCRIPTION, AMOUNT]

    @property
    def transactions(self) -> list[dict]:
        transactions = []
        for page in self.pages:
            for i, line in enumerate(page.lines):
                item = self._process_line(line, page.lines, idx=i)
                transactions.append(item)

        return list(filter(None, transactions))

    def _process_line(self, line: str, page: list[str], idx: int) -> dict:
        if match := re.match(self.transaction_pattern, line):
            date, description, amount = match.groups()

            if self.multiline_transactions:
                if not re.match(self.transaction_pattern, page[idx + 1]):
                    description = " ".join([description, page[idx + 1]])

            return {DATE: date, DESCRIPTION: description, AMOUNT: amount}
        return None

    @cached_property
    def statement_date(self):
        logger.info("Extracting statement date")
        first_page = self.pages[0]
        for line in first_page:
            if match := re.findall(self.date_pattern, line):
                statement_date = match[0]
                logger.debug("Statement date found")
                return datetime.strptime(statement_date, self.statement_date_format)
        return None

    def to_dataframe(self):
        return DataFrame(self.transactions, columns=self.columns)
