import logging
from re import compile as regex

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import ISO8601, BankNames, DebitTransactionPatterns, EntryType
from monopoly.identifiers import MetadataIdentifier

logger = logging.getLogger(__name__)


class ZurcherKantonalBank(BankBase):
    name = BankNames.ZKB

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=regex(rf"Balance as of: ({ISO8601.DD_MM_YYYY})"),
        header_pattern=regex(r"(Date.*Booking text.*Debit CHF.*Credit CHF)"),
        transaction_pattern=DebitTransactionPatterns.ZKB,
        multiline_config=MultilineConfig(multiline_descriptions=True),
        safety_check=False,
    )

    identifiers = [
        [
            MetadataIdentifier(
                format="PDF 1.7",
                title="SLK_Vermoegensinfo_Group",
                creator="Designer",
                producer="PDFlib+PDI",
            )
        ]
    ]
    statement_configs = [debit]
