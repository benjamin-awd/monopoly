import logging
from datetime import datetime

from monopoly.banks.bank import Bank, Pdf, Statement
from monopoly.config import settings
from monopoly.constants import DATE

logger = logging.getLogger(__name__)


class HsbcRevolution(Bank):
    statement_config = Statement(
        transaction_pattern=(
            r"\d{2}\s\w{3}\s*"
            r"(?P<date>\d{2}\s\w{3})\s*"
            r"(?P<description>.*?)\s*"
            r"(?P<amount>[\d.,]+)$"
        ),
        date_pattern=r"(\d{2}\s\w{3}\s\d{4})\s.*$",
        multiline_transactions=True,
    )

    def __init__(self, pdf_file_path: str):
        date_converter = self.convert_date
        super().__init__(
            account_name="Revolution",
            bank_name="HSBC",
            statement=Statement(**self.statement_config.__dict__),
            transform_dates=True,
            pdf=Pdf(
                pdf_file_path,
                settings.hsbc_pdf_password,
                page_range=(0, -1),
                page_bbox=(0, 0, 379, 842),
            ),
            date_converter=date_converter,
        )

    def convert_date(self, row):
        logger.info("Transforming dates to ISO 8601")
        split = row[DATE].split(" ")
        row_day = int(split[0])
        row_month = datetime.strptime(split[1], "%b").month

        # Deal with mixed years from Jan/Dec
        if self.statement.statement_date.month == 1 and row_month == 12:
            row_year = self.statement.statement_date.year - 1
        else:
            row_year = self.statement.statement_date.year

        return f"{row_year}-{row_month:02d}-{row_day:02d}"
