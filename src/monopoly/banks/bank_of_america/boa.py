import logging
from re import compile as regex

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import BankNames, CreditTransactionPatterns, EntryType
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier

logger = logging.getLogger(__name__)


class BankOfAmerica(BankBase):
    name = BankNames.BANK_OF_AMERICA

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=regex(rf"for .* to {ISO8601.MMMM_DD_YYYY}"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=regex(r"(Date.*Description.*Amount)"),
        transaction_pattern=CreditTransactionPatterns.BANK_OF_AMERICA,
        multiline_config=MultilineConfig(multiline_descriptions=True),
        safety_check=False,
        transaction_auto_polarity=False,
    )

    identifiers = [
        [
            MetadataIdentifier(
                format="PDF 1.5",
                creator="Bank of America",
                producer="TargetStream StreamEDS",
            )
        ]
    ]

    statement_configs = [credit]
