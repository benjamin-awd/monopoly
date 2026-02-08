import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class Dbs(BankBase):
    name = "dbs"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MMM_YYYY,
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        transaction_date_format="%d %b",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
        ),
        prev_balance_pattern=re.compile(
            r"(?P<description>PREVIOUS BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
    )

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=ISO8601.DD_MMM_YYYY,
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            description_margin=10,  # Allow for indented PayNow/transaction details
        ),
        header_pattern=re.compile(r"(WITHDRAWAL.*DEPOSIT.*BALANCE)"),
        transaction_date_format="%d %b",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_bound=170,
    )

    consolidated = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"Details as at {ISO8601.DD_MMM_YYYY}"),
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            description_margin=10,  # Allow for indented PayNow/transaction details
        ),
        header_pattern=re.compile(r"(\s*Date\s+Description\s+Withdrawal.*)"),
        transaction_date_format="%d/%m/%Y",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MM_YYYY})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_bound=220,
    )

    identifiers = [
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="Quadient CXM AG"),
        ],
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="Quadient"),
        ],
    ]

    statement_configs = [credit, consolidated, debit]
