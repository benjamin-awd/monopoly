import logging
from re import compile as regex

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import BankNames, CreditTransactionPatterns, EntryType
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class Chase(BankBase):
    name = BankNames.CHASE

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=regex(r"Statement Date:\s+(.*)"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=regex(r"(.*Transaction.*Merchant Name .*\$ Amount)"),
        transaction_pattern=CreditTransactionPatterns.CHASE,
        multiline_config=MultilineConfig(multiline_descriptions=True),
        transaction_auto_polarity=False,
    )

    identifiers = [
        [
            MetadataIdentifier(
                format="PDF 1.7",
                producer="OpenText Output Transformation Engine - 23.4",
            ),
            TextIdentifier("Chase"),
        ]
    ]

    statement_configs = [credit]
