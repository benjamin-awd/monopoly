import logging
from re import compile as regex

from monopoly.config import StatementConfig
from monopoly.constants import ISO8601, BankNames, CreditTransactionPatterns, EntryType
from monopoly.identifiers import TextIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class Trust(BankBase):
    name = BankNames.TRUST

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=regex(rf"\- {ISO8601.DD_MMM_YYYY}"),
        header_pattern=regex(r"(Posting date.*Description.*Amount in SGD)"),
        # prev_balance_pattern=StatementBalancePatterns.TRUST,
        transaction_pattern=CreditTransactionPatterns.TRUST,
        multiline_transactions=True,
        multiline_transactions_include_prev=True,
        multiline_transactions_include_prev_margin=99,
        safety_check=True,
    )

    identifiers = [[TextIdentifier("Trust Bank Singapore Limited")]]

    statement_configs = [credit]
