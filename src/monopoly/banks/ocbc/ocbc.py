import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PdfConfig, StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class Ocbc(BankBase):
    name = BankNames.OCBC

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MM_YYYY,
        header_pattern=re.compile(r"(TRANSACTION DATE.*DESCRIPTION.*AMOUNT)"),
        prev_balance_pattern=StatementBalancePatterns.OCBC,
        transaction_pattern=CreditTransactionPatterns.OCBC,
        transaction_date_format="%d/%m",
    )

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"\s{ISO8601.DD_MMM_YYYY}$"),
        header_pattern=re.compile(r"(Withdrawal.*Deposit.*Balance)"),
        transaction_pattern=DebitTransactionPatterns.OCBC,
        multiline_config=MultilineConfig(multiline_descriptions=True),
        transaction_bound=170,
        transaction_date_format="%d %b",
    )

    pdf_config = PdfConfig(
        remove_vertical_text=True,
    )

    identifiers = [
        [
            MetadataIdentifier(creator="pdfgen", producer="Streamline PDFGen for OCBC Group"),
            TextIdentifier("OCBC"),
        ],
    ]

    statement_configs = [credit, debit]
