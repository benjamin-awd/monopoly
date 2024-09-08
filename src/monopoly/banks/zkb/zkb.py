import logging
from re import compile as regex

from monopoly.config import StatementConfig
from monopoly.constants import BankNames, DebitTransactionPatterns, EntryType
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier

from ..base import BankBase

logger = logging.getLogger(__name__)


class ZurcherKantonalBank(BankBase):
    debit_config = StatementConfig(
        statement_type=EntryType.DEBIT,
        bank_name=BankNames.ZKB,
        statement_date_pattern=regex(rf"Balance as of: ({ISO8601.DD_MM_YYYY})"),
        header_pattern=regex(r"(Date.*Booking text.*Debit CHF.*Credit CHF)"),
        transaction_pattern=DebitTransactionPatterns.ZKB,
        multiline_transactions=True,
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
    statement_configs = [debit_config]
