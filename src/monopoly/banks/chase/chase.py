import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import BankNames, CreditTransactionPatterns, EntryType
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class Chase(BankBase):
    name = BankNames.CHASE

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(r"Statement Date:\s+(.*)"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(.*Transaction.*Merchant Name .*\$ Amount)"),
        transaction_date_format="%m/%d",
        transaction_pattern=CreditTransactionPatterns.CHASE,
        multiline_config=MultilineConfig(multiline_descriptions=True),
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
