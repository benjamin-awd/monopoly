import logging

from monopoly.config import CreditStatementConfig, DebitStatementConfig, passwords
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EncryptionIdentifier,
    MetadataIdentifier,
    StatementBalancePatterns,
)

from ..base import BankBase

logger = logging.getLogger(__name__)


class Ocbc(BankBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.OCBC,
        statement_date_pattern=r"(\d{2}\-\d{2}\-\d{4})",
        prev_balance_pattern=StatementBalancePatterns.OCBC,
        transaction_pattern=CreditTransactionPatterns.OCBC,
    )

    debit_config = DebitStatementConfig(
        bank_name=BankNames.OCBC,
        statement_date_pattern=r"TO\s(\d+\s[A-Za-z]{3}\s\d{4})",
        debit_statement_identifier=r"(Withdrawal.*Deposit.*Balance)",
        transaction_pattern=DebitTransactionPatterns.OCBC,
        multiline_transactions=True,
    )

    identifiers = [
        EncryptionIdentifier(
            pdf_version=1.4, algorithm=4, revision=4, length=128, permissions=-1036
        ),
        MetadataIdentifier(
            creator="pdfgen", producer="Streamline PDFGen for OCBC Group"
        ),
    ]

    passwords = passwords.ocbc_pdf_passwords
