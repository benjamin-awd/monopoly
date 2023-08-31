import logging

from monopoly.banks.dataclasses import Bank, Pdf, Statement
from monopoly.config import settings
from monopoly.constants import DATE

logger = logging.getLogger(__name__)


class Ocbc365(Bank):
    def __init__(self, pdf_file_path: str):
        date_converter = self.convert_date
        super().__init__(
            account_name="365",
            bank="OCBC",
            statement=Statement(
                transaction_pattern=r"(\d+\/\d+)\s*(.*?)\s*([\d.,]+)$",
                date_pattern=r"\d{2}\-\d{2}\-\d{4}",
            ),
            transform_dates=True,
            pdf=Pdf(pdf_file_path, settings.ocbc_pdf_password, (0, -2)),
            date_converter=date_converter,
        )

    def convert_date(self, row):
        logger.info("Transforming dates to ISO 8601")

        row_day, row_month = map(int, row[DATE].split("/"))

        # Deal with mixed years from Jan/Dec
        if self.statement.statement_date.month == 1 and row_month == 12:
            row_year = self.statement.statement_date.year - 1
        else:
            row_year = self.statement.statement_date.year

        return f"{row_year}-{row_month:02d}-{row_day:02d}"
