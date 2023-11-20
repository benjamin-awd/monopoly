import logging

from monopoly.config import PdfConfig, StatementConfig, TransactionConfig, settings
from monopoly.constants import (
    AccountType,
    BankNames,
    MetadataIdentifier,
    TransactionPatterns,
    StatementBalancePatterns,
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class StandardChartered(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.STANDARD_CHARTERED,
        account_type=AccountType.CREDIT,
        statement_date_pattern=r"\d{2}\s\w+\s\d{4}",
        statement_date_format=r"%d %B %Y",
        prev_balance_pattern=StatementBalancePatterns.STANDARD_CHARTERED,
    )

    transaction_config = TransactionConfig(
        pattern=TransactionPatterns.STANDARD_CHARTERED,
        date_format="%d %b",
    )

    pdf_config = PdfConfig(
        password=settings.standard_chartered_pdf_password,
        page_range=(0, -1),
        page_bbox=(0, 0, 580, 820),
    )

    identifiers = [
        MetadataIdentifier(
            title="eStatement",
            producer="iText",
        )
    ]
