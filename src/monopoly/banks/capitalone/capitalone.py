import re

from monopoly.banks import BankBase
from monopoly.config import StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    EntryType,
)
from monopoly.constants.statement import SharedPatterns
from monopoly.identifiers import MetadataIdentifier


class CapitalOneCanada(BankBase):
    name = BankNames.CAPITAL_ONE
    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"(\s+)?Transaction Date\s+Posting Date\s+Description\s+Amount"),
        statement_date_pattern=re.compile(rf" - (?P<statement_date>{ISO8601.MMM_DD_YYYY})"),
        transaction_pattern=re.compile(
            r"^\s*"
            rf"(?P<transaction_date>{ISO8601.MMM_DD})\s+"
            rf"(?P<posting_date>{ISO8601.MMM_DD})\s+"
            f"{SharedPatterns.DESCRIPTION}"
            rf"(?P<polarity>-)?\s*\$"
            rf"(?P<amount>{SharedPatterns.COMMA_FORMAT})\s*$"
        ),
    )
    identifiers = [
        [
            MetadataIdentifier(
                author="Registered to: CAPITAL1", title="Card_Statement_Canada", creator="OpenText Exstream"
            )
        ]
    ]

    statement_configs = [credit]
