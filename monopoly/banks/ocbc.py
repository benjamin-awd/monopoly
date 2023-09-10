import logging

from monopoly.bank import BankBase, StatementConfig
from monopoly.config import settings
from monopoly.pdf import PdfConfig

logger = logging.getLogger(__name__)


class Ocbc(BankBase):
    statement_config = StatementConfig(
        bank_name="OCBC",
        account_type="Credit",
        transaction_pattern=(
            r"(?P<date>\d+/\d+)\s*(?P<description>.*?)\s*(?P<amount>[\d.,]+)$"
        ),
        transaction_date_format="%d/%m",
        date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        statement_date_format=r"%d-%m-%Y",
    )

    pdf_config = PdfConfig(password=settings.ocbc_pdf_password, page_range=(0, -2))
