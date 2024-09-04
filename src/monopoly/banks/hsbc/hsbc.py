import logging
from re import compile as regex

from monopoly.config import PdfConfig, StatementConfig
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Hsbc(BankBase):
    credit_config = StatementConfig(
        statement_type=EntryType.CREDIT,
        bank_name=BankNames.HSBC,
        statement_date_pattern=regex(r"Statement From .* to (\d{2}\s[A-Z]{3}\s\d{4})"),
        header_pattern=regex(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        prev_balance_pattern=StatementBalancePatterns.HSBC,
        transaction_pattern=CreditTransactionPatterns.HSBC,
        multiline_transactions=True,
    )

    email_statement_identifier = [
        MetadataIdentifier(
            title="PRJ_BEAGLE_ST_CNS_SGH_APP_Orchid",
            author="Registered to: HSBCGLOB",
            creator="OpenText Exstream",
        ),
        TextIdentifier("HSBC"),
    ]

    web_and_mobile_statement_identifier = [
        MetadataIdentifier(
            format="PDF 1.7", producer="OpenText Output Transformation Engine"
        )
    ]

    pdf_config = PdfConfig(
        page_bbox=(0, 0, 379, 840),
        ocr_identifiers=web_and_mobile_statement_identifier,
    )

    identifiers = [email_statement_identifier, web_and_mobile_statement_identifier]

    statement_configs = [credit_config]
