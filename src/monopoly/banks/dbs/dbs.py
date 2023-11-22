import logging

from monopoly.config import PdfConfig, StatementConfig, TransactionConfig
from monopoly.constants import (
    AccountType,
    BankNames,
    EncryptionIdentifier,
    MetadataIdentifier,
    StatementBalancePatterns,
    TransactionPatterns,
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class Dbs(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.DBS,
        account_type=AccountType.CREDIT,
        date_pattern=r"(\d{2}\s[A-Za-z]{3}\s\d{4})",
        date_format=r"%d %b %Y",
        prev_balance_pattern=StatementBalancePatterns.DBS,
    )

    transaction_config = TransactionConfig(
        pattern=TransactionPatterns.DBS,
        date_format="%d %b",
    )

    pdf_config = PdfConfig(page_range=(0, -1))

    identifiers = [
        EncryptionIdentifier(
            pdf_version=1.4, algorithm=2, revision=3, length=128, permissions=-1852
        ),
        MetadataIdentifier(creator="Quadient CXM AG"),
    ]
