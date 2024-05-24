import logging

from monopoly.config import CreditStatementConfig, PdfConfig, passwords
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    MetadataIdentifier,
    StatementBalancePatterns,
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class StandardChartered(BankBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.STANDARD_CHARTERED,
        statement_date_pattern=r"(\d{2}\s\w+\s\d{4})",
        prev_balance_pattern=StatementBalancePatterns.STANDARD_CHARTERED,
        transaction_pattern=CreditTransactionPatterns.STANDARD_CHARTERED,
    )

    pdf_config = PdfConfig(
        page_range=(0, -1),
        page_bbox=(0, 0, 580, 820),
    )

    identifiers = [
        MetadataIdentifier(
            title="eStatement",
            producer="iText",
        )
    ]

    passwords = passwords.standard_chartered_pdf_passwords
