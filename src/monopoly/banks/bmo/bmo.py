import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

MMM_DOT_DD = r"[A-Z][a-z]{2,3}\.\s+\d{1,2}"
MMM_DOT_DD_YYYY = r"[A-Z][a-z]{2,3}\.\s+\d{1,2},\s+\d{4}"


class BankOfMontreal(BankBase):
    name = "bmo"

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"For the period ending.*{ISO8601.MMMM_DD_YYYY}"),
        header_pattern=re.compile(
            r"Date\s+Description\s+from\ your\ account\ \(\$\)\s+to\ your\ account\ \(\$\)\s+Balance\ \(\$\)"
        ),
        transaction_pattern=re.compile(
            rf"^(?!.*(?:Closing totals)).*?"
            rf"(?P<transaction_date>{ISO8601.MMM_DD})\s+"
            rf"{SharedPatterns.DESCRIPTION}\s+"
            rf"(?P<amount>{SharedPatterns.COMMA_FORMAT})\s+"
            rf"(?P<balance>{SharedPatterns.COMMA_FORMAT})$"
        ),
        transaction_date_format="%b %d",
        multiline_config=MultilineConfig(multiline_descriptions=True, multiline_transaction_date=True),
    )
    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"Statement\s+date\s+(?P<statement_date>{MMM_DOT_DD_YYYY})"),
        header_pattern=re.compile(r"DATE\s+DATE\s+DESCRIPTION\s+AMOUNT\ \(\$\)"),
        transaction_pattern=re.compile(
            r"(?P<transaction_date>[A-Z][a-z]{2,3}\.\s+\d{1,2})\s+"
            r"(?P<posting_date>[A-Z][a-z]{2,3}\.\s+\d{1,2})\s+"
            r"(?P<description>.+?)\s+"
            r"(?P<amount>\d{1,3}(?:,\d{3})*\.\d{2})(\s+)?"
            r"(?P<polarity>CR)?$"
        ),
        transaction_date_format="%b. %d",
    )

    identifiers = [
        # DR
        [
            TextIdentifier(text="www.bmo.com"),  # debit
        ],
        # CR personal
        [MetadataIdentifier(title="BMO Personal")],
        # CR business
        [MetadataIdentifier(title="BMO Small Business Statements")],
    ]

    statement_configs = [debit, credit]
