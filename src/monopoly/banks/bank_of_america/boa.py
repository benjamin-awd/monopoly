import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
)
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier

logger = logging.getLogger(__name__)


class BankOfAmerica(BankBase):
    name = BankNames.BANK_OF_AMERICA

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"for .* to {ISO8601.MMMM_DD_YYYY}"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(Date\s+Description\s+Amount)"),
        transaction_pattern=DebitTransactionPatterns.BANK_OF_AMERICA,
        transaction_date_format="%m/%d/%y",
        multiline_config=MultilineConfig(multiline_descriptions=True),
        safety_check=False,
    )

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"Statement Closing Date\s+{ISO8601.MM_DD_YYYY}"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(Date\s+Date\s+Description\s+Number\s+Number\s+Amount\s+Total)"),
        transaction_pattern=CreditTransactionPatterns.BANK_OF_AMERICA,
        transaction_date_format="%m/%d",
        multiline_config=MultilineConfig(multiline_descriptions=True),
        safety_check=False,
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

    statement_configs = [debit, credit]
