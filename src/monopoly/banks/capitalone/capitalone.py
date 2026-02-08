import re

from monopoly.banks.base import BankBase
from monopoly.config import StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601, DateFormats
from monopoly.identifiers import MetadataIdentifier


class CapitalOneCanada(BankBase):
    name = "capital_one"
    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"(\s+)?Transaction Date\s+Posting Date\s+Description\s+Amount"),
        statement_date_pattern=re.compile(rf" - (?P<statement_date>{ISO8601.MMM_DD_YYYY})"),
        transaction_pattern=re.compile(
            r"^\s*"
            rf"(?P<transaction_date>\b({DateFormats.MMM}\s+{DateFormats.D}))\s+"
            rf"(?P<posting_date>\b({DateFormats.MMM}\s+{DateFormats.D}))\s+"
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
