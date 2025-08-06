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


class Maybank(BankBase):
    name = BankNames.MAYBANK

    my_debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"(?:結單日期)[:\s]+{ISO8601.DD_MM_YY}"),
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT.*BALANCE)"),
        transaction_date_format="%d/%m/%y",
        transaction_pattern=DebitTransactionPatterns.MAYBANK_MY,
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    my_credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MMM_YY,
        header_pattern=re.compile(r"(Date.*Description.*Amount)"),
        transaction_date_format="%d/%m",
        transaction_pattern=CreditTransactionPatterns.MAYBANK_MY,
        prev_balance_pattern=StatementBalancePatterns.MAYBANK_MY,
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    sg_credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(f"AS AT {ISO8601.DD_MMM_YYYY}"),
        header_pattern=re.compile(r"(.*DESCRIPTION OF TRANSACTION.*TRANSACTION AMOUNT)"),
        transaction_pattern=CreditTransactionPatterns.MAYBANK_SG,
        prev_balance_pattern=StatementBalancePatterns.MAYBANK_SG,
    )

    sg_credit_identifier = [[TextIdentifier("maybank2u.com.sg"), TextIdentifier("PAYMENT DUE")]]

    identifiers = [
        *sg_credit_identifier,
        [
            MetadataIdentifier(
                author="Maybank2U.com",
                creator="Maybank2u.com",
                producer="iText",
            ),
        ],
        [
            MetadataIdentifier(
                title="Credit Card Statement",
                author="Maybank2U.com",
                producer="iText",
            ),
        ],
    ]

    pdf_config = PdfConfig(
        ocr_identifiers=sg_credit_identifier,
    )

    statement_configs = [my_credit, my_debit, sg_credit]
