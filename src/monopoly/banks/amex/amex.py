import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import TextIdentifier

logger = logging.getLogger(__name__)


class Amex(BankBase):
    name = "amex"

    platinum = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"From .* to {ISO8601.DD_MM_YYYY}"),
        transaction_date_format="%d.%m.%y",
        header_pattern=re.compile(r"(Details.*Foreign Spending.*Amount)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MM_YY})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED
        ),
        multiline_config=MultilineConfig(multiline_polarity=True),
    )
    identifiers = [
        [
            TextIdentifier("The Platinum Credit Card"),
            TextIdentifier("americanexpress.com"),
        ]
    ]

    statement_configs = [platinum]
