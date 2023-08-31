import logging

from monopoly.banks.statement import BankStatement
from monopoly.config import settings
from monopoly.constants import DATE

logger = logging.getLogger(__name__)


class Ocbc365(BankStatement):
    def __init__(self, pdf_file_path: str):
        date_converter = self.convert_date
        super().__init__(
            account_name="365",
            bank="OCBC",
            date_pattern=r"\d{2}\-\d{2}\-\d{4}",
            transaction_pattern=r"(\d+\/\d+)\s*(.*?)\s*([\d.,]+)$",
            transform_dates=True,
            pdf_file_path=pdf_file_path,
            pdf_page_range=(0, -2),
            pdf_password=settings.ocbc_pdf_password,
            statement_date=None,
            date_converter=date_converter,
        )

    def convert_date(self, row):
        logger.info("Transforming dates to ISO 8601")

        row_day, row_month = map(int, row[DATE].split("/"))

        # Deal with mixed years from Jan/Dec
        if self.statement_date.month == 1 and row_month == 12:
            row_year = self.statement_date.year - 1
        else:
            row_year = self.statement_date.year

        return f"{row_year}-{row_month:02d}-{row_day:02d}"
