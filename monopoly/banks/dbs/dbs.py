import logging

from monopoly.config import PdfConfig, StatementConfig
from monopoly.constants import (
    AccountType,
    BankNames,
    EncryptionIdentifier,
    MetadataIdentifier,
    TransactionPatterns,
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class Dbs(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.DBS,
        account_type=AccountType.CREDIT,
        transaction_pattern=TransactionPatterns.DBS,
        transaction_date_format="%d %b",
        statement_date_pattern=r"(\d{2}\s[A-Za-z]{3}\s\d{4})",
        statement_date_format=r"%d %b %Y",
    )

    pdf_config = PdfConfig(page_range=(0, -1))

    identifiers = [
        EncryptionIdentifier(
            pdf_version=1.4, algorithm=2, revision=3, length=128, permissions=-1852
        ),
        MetadataIdentifier(creator="Quadient CXM AG"),
    ]
