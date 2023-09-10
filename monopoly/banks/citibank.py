import logging

from monopoly.bank import BankBase, StatementConfig
from monopoly.pdf import PdfConfig

logger = logging.getLogger(__name__)


class Citibank(BankBase):
    statement_config = StatementConfig(
        bank_name="Citibank",
        account_type="Credit",
        transaction_pattern=(
            r"(?P<date>\b\d{2}\s\w{3}\b)\s*(?P<description>.*?)\s*(?P<amount>[\d.,]+)$"
        ),
        transaction_date_format="%d %b",
        date_pattern=r"Statement\sDate\s(.*)$",
        statement_date_format=r"%B %d, %Y",
    )

    pdf_config = PdfConfig(page_range=(0, -3))
