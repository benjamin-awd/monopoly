import logging

from monopoly.config import BruteForceConfig, PdfConfig, StatementConfig, settings
from monopoly.constants import (
    AccountType,
    BankNames,
    EncryptionIdentifier,
    MetadataIdentifier,
    TransactionPatterns,
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class Hsbc(BankBase):
    statement_config = StatementConfig(
        bank_name=BankNames.HSBC,
        account_type=AccountType.CREDIT,
        transaction_pattern=TransactionPatterns.HSBC,
        transaction_date_format="%d %b",
        statement_date_pattern=r"(\d{2}\s[A-Z]{3}\s\d{4})\s.*$",
        multiline_transactions=True,
        statement_date_format=r"%d %b %Y",
    )

    pdf_config = PdfConfig(
        password=settings.hsbc_pdf_password,
        page_range=(0, -1),
        page_bbox=(0, 0, 379, 842),
    )

    brute_force_config = BruteForceConfig(
        static_string=settings.hsbc_pdf_password_prefix, mask="?d?d?d?d?d?d"
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
