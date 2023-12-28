import logging

from monopoly.config import CreditStatementConfig, PdfConfig, settings
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    EncryptionIdentifier,
    MetadataIdentifier,
    StatementBalancePatterns,
)

from ..base import ProcessorBase

logger = logging.getLogger(__name__)


class Hsbc(ProcessorBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.HSBC,
        statement_date_pattern=r"Statement From (\d{2}\s[A-Z]{3}\s\d{4}) to",
        prev_balance_pattern=StatementBalancePatterns.HSBC,
        statement_date_format=r"%d %b %Y",
        transaction_pattern=CreditTransactionPatterns.HSBC,
        transaction_date_format="%d %b",
        multiline_transactions=True,
    )

    pdf_config = PdfConfig(
        passwords=settings.hsbc_pdf_passwords,
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
