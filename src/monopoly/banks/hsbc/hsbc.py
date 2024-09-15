import logging
from re import compile as regex

from monopoly.config import PdfConfig, StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    CreditTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Hsbc(BankBase):
    name = BankNames.HSBC

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=regex(rf"Statement From .* to {ISO8601.DD_MMM_YYYY}"),
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

    statement_configs = [credit]
