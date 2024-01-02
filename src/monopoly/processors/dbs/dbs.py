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

from ..base import ProcessorBase

logger = logging.getLogger(__name__)


class Dbs(ProcessorBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.DBS,
        statement_date_pattern=r"(\d{2}\s[A-Za-z]{3}\s\d{4})",
        statement_date_format=r"%d %b %Y",
        transaction_date_format=r"%d %b",
        multiline_transactions=True,
        transaction_pattern=CreditTransactionPatterns.DBS,
        prev_balance_pattern=StatementBalancePatterns.DBS,
    )

    debit_config = DebitStatementConfig(
        bank_name=BankNames.DBS,
        statement_date_pattern=r"(\d{2}\s[A-Za-z]{3}\s\d{4})",
        statement_date_format=r"%d %b %Y",
        transaction_date_format=r"%d %b",
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
