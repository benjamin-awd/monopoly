import logging

from monopoly.banks.bank import Bank, Pdf, Statement
from monopoly.config import settings

logger = logging.getLogger(__name__)


class HsbcRevolution(Bank):
    def __init__(self, pdf_file_path: str):
        super().__init__(
            account_name="Revolution",
            bank_name="HSBC",
            statement=Statement(
                transaction_pattern=(
                    r"\d{2}\s\w{3}\s*(\d{2}\s\w{3})\s*(.*?)\s*([\d.,]+)$"
                ),
                date_pattern=r"(\d{2}\s\w{3}\s\d{4})\s.*$",
                multiline_transactions=True,
            ),
            transform_dates=True,
            pdf=Pdf(
                pdf_file_path,
                settings.hsbc_pdf_password,
                page_range=(0, -1),
                page_bbox=(0, 0, 379, 842),
            ),
        )
