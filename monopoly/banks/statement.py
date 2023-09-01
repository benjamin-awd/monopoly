import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Match

import fitz
from pandas import DataFrame

from monopoly.constants import AMOUNT, DATE, DESCRIPTION

logger = logging.getLogger(__name__)


@dataclass
class Statement:
    transaction_pattern: Match
    date_pattern: Match
    pages: list[fitz.Page] = None
    columns = [DATE, DESCRIPTION, AMOUNT]

    @property
    def transactions(self):
        transactions = []
        for page in self.pages:
            for line in page:
                if match := re.match(self.transaction_pattern, line):
                    date, description, amount = match.groups()

                    transactions.append(
                        {DATE: date, DESCRIPTION: description, AMOUNT: amount}
                    )
        return transactions

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
