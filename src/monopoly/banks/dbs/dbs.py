import logging

from monopoly.config import CreditStatementConfig, DebitStatementConfig
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


class Dbs(BankBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.DBS,
        statement_date_pattern=r"(\d{2}\s[A-Za-z]{3}\s\d{4})",
        multiline_transactions=False,
        transaction_pattern=CreditTransactionPatterns.DBS,
        prev_balance_pattern=StatementBalancePatterns.DBS,
    )

    debit_config = DebitStatementConfig(
        bank_name=BankNames.DBS,
        statement_date_pattern=r"(\d{2}\s[A-Za-z]{3}\s\d{4})",
        multiline_transactions=True,
        debit_statement_identifier=r"(WITHDRAWAL.*DEPOSIT.*BALANCE)",
        transaction_pattern=DebitTransactionPatterns.DBS,
    )

    identifiers = [
        EncryptionIdentifier(
            pdf_version=1.4, algorithm=2, revision=3, length=128, permissions=-1852
        ),
        MetadataIdentifier(creator="Quadient CXM AG"),
    ]
