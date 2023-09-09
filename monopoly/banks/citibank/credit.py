import logging
from datetime import datetime

from monopoly.banks.bank import BankBase, StatementConfig
from monopoly.constants import DATE
from monopoly.pdf import PdfConfig

logger = logging.getLogger(__name__)


class Citibank(BankBase):
    statement_config = StatementConfig(
        bank_name="Citibank",
        account_type="Credit",
        transaction_pattern=(
            r"(?P<date>\b\d{2}\s\w{3}\b)\s*(?P<description>.*?)\s*(?P<amount>[\d.,]+)$"
        ),
        date_pattern=r"Statement\sDate\s(.*)$",
        statement_date_format=r"%B %d, %Y",
    )

    pdf_config = PdfConfig(page_range=(0, -3))

    def __init__(self, file_path: str):
        super().__init__(file_path, self.get_date_parts)

    def get_date_parts(self, row):
        split = row[DATE].split(" ")
        row_day = int(split[0])
        row_month = datetime.strptime(split[1], "%b").month
        return row_day, row_month
