import logging
from re import compile as regex

from monopoly.config import StatementConfig
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Ocbc(BankBase):
    credit_config = StatementConfig(
        statement_type=EntryType.CREDIT,
        bank_name=BankNames.OCBC,
        statement_date_pattern=regex(r"(\d{2}\-\d{2}\-\d{4})"),
        header_pattern=regex(r"(TRANSACTION DATE.*DESCRIPTION.*AMOUNT)"),
        prev_balance_pattern=StatementBalancePatterns.OCBC,
        transaction_pattern=CreditTransactionPatterns.OCBC,
    )

    debit_config = StatementConfig(
        statement_type=EntryType.DEBIT,
        bank_name=BankNames.OCBC,
        statement_date_pattern=regex(r"TO\s(\d+\s[A-Za-z]{3}\s\d{4})"),
        header_pattern=regex(r"(Withdrawal.*Deposit.*Balance)"),
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

    statement_configs = [debit_config, credit_config]
