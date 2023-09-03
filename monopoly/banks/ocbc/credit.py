import logging

from monopoly.banks.bank import BankBase, StatementConfig
from monopoly.config import settings
from monopoly.constants import DATE
from monopoly.pdf import PdfConfig

logger = logging.getLogger(__name__)


class Ocbc365(BankBase):
    statement_config = StatementConfig(
        bank_name="OCBC",
        account_name="365",
        transaction_pattern=(
            r"(?P<date>\d+/\d+)\s*(?P<description>.*?)\s*(?P<amount>[\d.,]+)$"
        ),
        date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        statement_date_format=r"%d-%m-%Y",
    )

    pdf_config = PdfConfig(password=settings.ocbc_pdf_password, page_range=(0, -2))

    def __init__(self, file_path: str):
        super().__init__(file_path, self.get_date_parts)

    def get_date_parts(self, row):
        row_day, row_month = map(int, row[DATE].split("/"))
        return row_day, row_month
