import logging

from monopoly.config import PdfConfig, StatementConfig, settings
from monopoly.constants import AccountType, BankNames, TransactionPatterns

from ..base import BankBase

logger = logging.getLogger(__name__)


class Ocbc(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.OCBC,
        account_type=AccountType.CREDIT,
        transaction_pattern=TransactionPatterns.OCBC,
        transaction_date_format="%d/%m",
        statement_date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        statement_date_format=r"%d-%m-%Y",
    )

    pdf_config = PdfConfig(
        password=settings.ocbc_pdf_password,
        page_range=(0, -2),
        page_bbox=(0, 0, 560, 750),
    )
