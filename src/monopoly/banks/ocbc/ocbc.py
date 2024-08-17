import logging

from monopoly.config import CreditStatementConfig, DebitStatementConfig
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Ocbc(BankBase):
    credit_config = CreditStatementConfig(
        bank_name=BankNames.OCBC,
        statement_date_pattern=r"(\d{2}\-\d{2}\-\d{4})",
        header_pattern=r"(TRANSACTION DATE.*DESCRIPTION.*AMOUNT)",
        prev_balance_pattern=StatementBalancePatterns.OCBC,
        transaction_pattern=CreditTransactionPatterns.OCBC,
    )

    debit_config = DebitStatementConfig(
        bank_name=BankNames.OCBC,
        statement_date_pattern=r"TO\s(\d+\s[A-Za-z]{3}\s\d{4})",
        header_pattern=r"(Withdrawal.*Deposit.*Balance)",
        transaction_pattern=DebitTransactionPatterns.OCBC,
        multiline_transactions=True,
    )

    identifiers = [
        [
            MetadataIdentifier(
                creator="pdfgen", producer="Streamline PDFGen for OCBC Group"
            ),
            TextIdentifier("OCBC"),
        ],
    ]
