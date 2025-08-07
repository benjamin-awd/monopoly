import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import BankNames, CreditTransactionPatterns, EntryType
from monopoly.constants.date import ISO8601
from monopoly.identifiers import TextIdentifier

logger = logging.getLogger(__name__)


class Amex(BankBase):
    name = BankNames.AMEX

    platinum = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"From .* to {ISO8601.DD_MM_YYYY}"),
        transaction_date_format="%d.%m.%y",
        header_pattern=re.compile(r"(Details.*Foreign Spending.*Amount)"),
        transaction_pattern=CreditTransactionPatterns.AMEX_PLATINUM,
        multiline_config=MultilineConfig(multiline_polarity=True),
    )
    identifiers = [
        [
            TextIdentifier("The Platinum Credit Card"),
            TextIdentifier("americanexpress.com"),
        ]
    ]

    statement_configs = [platinum]
