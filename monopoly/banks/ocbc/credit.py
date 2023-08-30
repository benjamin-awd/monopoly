import logging

from monopoly.banks.statement import BankStatement
from monopoly.config import settings

logger = logging.getLogger(__name__)


class Ocbc365(BankStatement):
    def __init__(self, pdf_file_path: str):
        super().__init__(
            account_name="365",
            bank="OCBC",
            date_pattern=r"\d{2}\-\d{2}\-\d{4}",
            transaction_pattern=r"(\d+\/\d+)\s*(.*?)\s*([\d.,]+)$",
            transform_dates=True,
            pdf_file_path=pdf_file_path,
            pdf_page_range=(0, -2),
            pdf_password=settings.ocbc_pdf_password,
        )
