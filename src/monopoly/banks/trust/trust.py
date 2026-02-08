import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import TextIdentifier

logger = logging.getLogger(__name__)


class Trust(BankBase):
    name = "trust"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(
            r"-\s*"
            r"(?P<day>\d{2})\s+"
            r"(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
            r".*?"
            r"(?P<year>20\d{2}\b)"
        ),
        header_pattern=re.compile(r"(Posting date.*Description.*Amount in SGD)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            rf"(?:{ISO8601.DD_MMM}\s+)?"  # Optional posting date
            r"(?P<description>(?:(?!Total outstanding balance).)*?)"
            r"(?P<polarity>\+)?"
            f"{SharedPatterns.AMOUNT}"
            r"$"  # necessary to ignore FCY
        ),
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            include_prev_margin=99,
            multiline_statement_date=True,
        ),
        safety_check=True,
        transaction_date_format="%d %b",
    )

    identifiers = [[TextIdentifier("Trust Bank Singapore Limited")]]

    statement_configs = [credit]
