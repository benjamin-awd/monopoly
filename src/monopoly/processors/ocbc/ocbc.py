import logging

from monopoly.config import (
    CreditStatementConfig,
    DebitStatementConfig,
    PdfConfig,
    settings,
)
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EncryptionIdentifier,
    MetadataIdentifier,
    StatementBalancePatterns,
)

from ..base import ProcessorBase

logger = logging.getLogger(__name__)


class Ocbc(ProcessorBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.OCBC,
        statement_date_pattern=r"(\d{2}\-\d{2}\-\d{4})",
        statement_date_order="DMY",
        prev_balance_pattern=StatementBalancePatterns.OCBC,
        transaction_pattern=CreditTransactionPatterns.OCBC,
        transaction_date_order="DMY",
    )

    debit_config = DebitStatementConfig(
        bank_name=BankNames.OCBC,
        statement_date_pattern=r"(\d+\s[A-Za-z]{3}\s\d{4})",
        debit_statement_identifier=r"(Withdrawal.*Deposit.*Balance)",
        transaction_pattern=DebitTransactionPatterns.OCBC,
        multiline_transactions=True,
    )

    pdf_config = PdfConfig(
        passwords=settings.ocbc_pdf_passwords,
    )

    identifiers = [
        EncryptionIdentifier(
            pdf_version=1.4, algorithm=4, revision=4, length=128, permissions=-1036
        ),
        MetadataIdentifier(
            creator="pdfgen", producer="Streamline PDFGen for OCBC Group"
        ),
    ]
