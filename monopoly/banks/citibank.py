import logging

from monopoly.bank import BankBase, StatementConfig
from monopoly.config import settings
from monopoly.helpers.constants import AccountType, BankNames
from monopoly.pdf import PdfConfig

logger = logging.getLogger(__name__)


class Citibank(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.CITIBANK,
        account_type=AccountType.CREDIT,
        transaction_pattern=(
            r"(?P<date>\b\d{2}\s\w{3}\b)\s*(?P<description>.*?)\s*(?P<amount>[\d.,]+)$"
        ),
        transaction_date_format="%d %b",
        date_pattern=r"Statement\sDate\s(.*)$",
        statement_date_format=r"%B %d, %Y",
    )

    pdf_config = PdfConfig(password=settings.citibank_pdf_password, page_range=(0, -3))
