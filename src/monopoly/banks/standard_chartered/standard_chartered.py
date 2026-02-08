import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class StandardChartered(BankBase):
    name = "standard_chartered"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf": {ISO8601.DD_MMM_YYYY}$"),
        header_pattern=re.compile(r"(Transaction.*Posting.*Amount)"),
        prev_balance_pattern=re.compile(
            r"(?P<description>BALANCE FROM PREVIOUS STATEMENT?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?:(?P<transaction_ref>Transaction\sRef\s\d+)?)\s+"
            + SharedPatterns.AMOUNT_EXTENDED
        ),
        transaction_date_format="%d %b",
    )

    identifiers = [
        [
            MetadataIdentifier(
                title="eStatement",
                producer="iText",
            ),
            TextIdentifier("Standard Chartered"),
        ]
    ]

    statement_configs = [credit]
