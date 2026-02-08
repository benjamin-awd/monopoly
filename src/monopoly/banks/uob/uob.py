import logging
import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

logger = logging.getLogger(__name__)


class Uob(BankBase):
    name = "uob"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"Statement Date.*{ISO8601.DD_MMM_YYYY}"),
        header_pattern=re.compile(r"(Description of Transaction.*Transaction Amount)"),
        prev_balance_pattern=re.compile(
            r"(?P<description>PREVIOUS BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=re.compile(
            rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
        ),
        multiline_config=MultilineConfig(multiline_descriptions=True),
        transaction_date_format="%d %b",
    )

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"Period: .* to {ISO8601.DD_MMM_YYYY}"),
        header_pattern=re.compile(r"(Date.*Description.*Withdrawals.*Deposits.*Balance)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
            + SharedPatterns.BALANCE
        ),
        transaction_bound=170,
        multiline_config=MultilineConfig(multiline_descriptions=True),
        transaction_date_format="%d %b",
    )

    identifiers = [
        [
            MetadataIdentifier(
                format="PDF 1.5",
                creator="Vault Rendering Engine",
                producer="Rendering Engine",
            ),
        ],
        [TextIdentifier("card.centre@uobgroup.com")],
    ]
    statement_configs = [credit, debit]
