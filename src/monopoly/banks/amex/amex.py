import logging
from re import compile as regex

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import BankNames, CreditTransactionPatterns, EntryType
from monopoly.constants.date import ISO8601
from monopoly.identifiers import TextIdentifier

logger = logging.getLogger(__name__)


class Amex(BankBase):
    name = BankNames.AMEX

    platinum = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=regex(rf"From .* to {ISO8601.DD_MM_YYYY}"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=regex(r"(Details.*Foreign Spending.*Amount)"),
        transaction_pattern=CreditTransactionPatterns.AMEX_PLATINUM,
        multiline_config=MultilineConfig(multiline_polarity=True),
        safety_check=False,
    )
    identifiers = [
        [
            TextIdentifier("The Platinum Credit Card"),
            TextIdentifier("americanexpress.com"),
        ]
    ]

    statement_configs = [platinum]
