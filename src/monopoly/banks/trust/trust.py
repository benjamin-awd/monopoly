import logging
from re import compile as regex

from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import BankNames, CreditTransactionPatterns, EntryType
from monopoly.identifiers import TextIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Trust(BankBase):
    name = BankNames.TRUST

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=regex(
            r"-\s*"
            r"(?P<day>\d{2})\s+"
            r"(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
            r".*?"
            r"(?P<year>20\d{2}\b)"
        ),
        header_pattern=regex(r"(Posting date.*Description.*Amount in SGD)"),
        # prev_balance_pattern=StatementBalancePatterns.TRUST,
        transaction_pattern=CreditTransactionPatterns.TRUST,
        multiline_config=MultilineConfig(
            multiline_transactions=True,
            include_prev_margin=99,
            multiline_statement_date=True,
        ),
        safety_check=True,
    )

    identifiers = [[TextIdentifier("Trust Bank Singapore Limited")]]

    statement_configs = [credit]
