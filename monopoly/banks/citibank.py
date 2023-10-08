import logging

from monopoly.bank import BankBase
from monopoly.config import PdfConfig, StatementConfig, settings
from monopoly.constants import AccountType, BankNames

logger = logging.getLogger(__name__)


class Citibank(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.CITIBANK,
        account_type=AccountType.CREDIT,
        transaction_pattern=(
            r"^(?P<date>\b\d{2}\s\w{3}\b)\s*(?P<description>.*?)\s*(?P<amount>[\d.,]+)$"
        ),
        transaction_date_format="%d %b",
        statement_date_pattern=r"Statement\sDate\s(.*)$",
        statement_date_format=r"%B %d, %Y",
    )

    pdf_config = PdfConfig(
        password=settings.citibank_pdf_password,
        page_bbox=(20, 0, 595, 840),
        page_range=(0, -3),
    )
