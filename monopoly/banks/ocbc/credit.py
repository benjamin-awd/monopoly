import logging

from monopoly.banks.bank import Bank, Pdf, Statement
from monopoly.config import settings
from monopoly.constants import DATE

logger = logging.getLogger(__name__)


class Ocbc365(Bank):
    statement_config = Statement(
        transaction_pattern=(
            r"(?P<date>\d+/\d+)\s*(?P<description>.*?)\s*(?P<amount>[\d.,]+)$"
        ),
        date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        statement_date_format=r"%d-%m-%Y",
    )

    def __init__(self, pdf_file_path: str):
        date_parser = self.get_date_parts
        super().__init__(
            account_name="365",
            bank_name="OCBC",
            statement=Statement(**self.statement_config.__dict__),
            transform_dates=True,
            pdf=Pdf(pdf_file_path, settings.ocbc_pdf_password, (0, -2)),
            date_parser=date_parser,
        )

    def get_date_parts(self, row):
        row_day, row_month = map(int, row[DATE].split("/"))
        return row_day, row_month
