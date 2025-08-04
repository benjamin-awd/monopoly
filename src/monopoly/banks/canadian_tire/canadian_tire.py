import re

from monopoly.banks import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    EntryType,
)
from monopoly.constants.statement import CreditTransactionPatterns
from monopoly.identifiers import MetadataIdentifier


class CanadianTire(BankBase):
    name = BankNames.CANADIAN_TIRE

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"\s+DATE\s+DATE\s+TRANSACTION\ DESCRIPTION\s+AMOUNT\ \(\$\)"),
        statement_date_pattern=re.compile(rf"Statement\s+date\s+(?P<statement_date>{ISO8601.MMMM_DD_YYYY})"),
        transaction_pattern=CreditTransactionPatterns.CANADIAN_TIRE,
        transaction_date_format="%b %d",
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    identifiers = [[MetadataIdentifier(author="Canadian Tire Bank / Banque Canadian Tire", producer="PDFlib+PDI")]]

    statement_configs = [credit]
