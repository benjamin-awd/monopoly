import logging

from monopoly.bank import BankBase, StatementConfig
from monopoly.config import settings
from monopoly.helpers.constants import AccountType, BankNames
from monopoly.pdf import PdfConfig

logger = logging.getLogger(__name__)


class Hsbc(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.HSBC,
        account_type=AccountType.CREDIT,
        transaction_pattern=(
            r"\d{2}\s\w{3}\s*"
            r"(?P<date>\d{2}\s\w{3})\s.*?"
            r"(?P<description>\w.*?)\s*"
            r"(?P<amount>[\d.,]+)$"
        ),
        transaction_date_format="%d %b",
        date_pattern=r"(\d{2}\s\w{3}\s\d{4})\s.*$",
        multiline_transactions=True,
        statement_date_format=r"%d %b %Y",
    )

    pdf_config = PdfConfig(
        static_string=settings.hsbc_pdf_password_prefix,
        brute_force_mask="?d?d?d?d?d?d",
        page_range=(0, -1),
        page_bbox=(0, 0, 379, 842),
    )