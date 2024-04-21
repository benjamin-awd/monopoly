import logging

from monopoly.config import CreditStatementConfig, PdfConfig, settings
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    MetadataIdentifier,
    StatementBalancePatterns,
)

from ..base import ProcessorBase

logger = logging.getLogger(__name__)


class StandardChartered(ProcessorBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.STANDARD_CHARTERED,
        statement_date_pattern=r"(\d{2}\s\w+\s\d{4})",
        statement_date_format=r"%d %b %Y",
        prev_balance_pattern=StatementBalancePatterns.STANDARD_CHARTERED,
        transaction_pattern=CreditTransactionPatterns.STANDARD_CHARTERED,
        transaction_date_format="%d %b",
    )

    pdf_config = PdfConfig(
        passwords=settings.standard_chartered_pdf_passwords,
        page_range=(0, -1),
        page_bbox=(0, 0, 580, 820),
    )

    identifiers = [
        MetadataIdentifier(
            title="eStatement",
            producer="iText",
        )
    ]
