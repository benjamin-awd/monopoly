import logging

from monopoly.banks.bank import Bank, Pdf, Statement
from monopoly.config import settings

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
        )
