import logging

from monopoly.config import CreditStatementConfig, PdfConfig, passwords
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    EncryptionIdentifier,
    MetadataIdentifier,
    StatementBalancePatterns,
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class Hsbc(BankBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.HSBC,
        statement_date_pattern=r"Statement From .* to (\d{2}\s[A-Z]{3}\s\d{4})",
        prev_balance_pattern=StatementBalancePatterns.HSBC,
        transaction_pattern=CreditTransactionPatterns.HSBC,
        multiline_transactions=True,
    )

    pdf_config = PdfConfig(
        page_bbox=(0, 0, 379, 842),
    )

    identifiers = [
        EncryptionIdentifier(
            pdf_version=1.6, algorithm=4, revision=4, length=128, permissions=-1804
        ),
        MetadataIdentifier(
            title="PRJ_BEAGLE_ST_CNS_SGH_APP_Orchid",
            creator="OpenText Exstream",
        ),
    ]

    passwords = passwords.hsbc_pdf_passwords
