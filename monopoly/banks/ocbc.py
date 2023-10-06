import logging

from monopoly.bank import BankBase, StatementConfig
from monopoly.config import settings
from monopoly.helpers.constants import AccountType, BankNames
from monopoly.pdf import PdfConfig

logger = logging.getLogger(__name__)


class Ocbc(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.OCBC,
        account_type=AccountType.CREDIT,
        transaction_pattern=(
            r"(?P<date>\d+/\d+)\s*(?P<description>.*?)\s*(?P<amount>[\d.,]+)$"
        ),
        transaction_date_format="%d/%m",
        date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        statement_date_format=r"%d-%m-%Y",
    )

    pdf_config = PdfConfig(
        password=settings.ocbc_pdf_password,
        page_range=(0, -2),
        page_bbox=(0, 0, 560, 750),
    )
