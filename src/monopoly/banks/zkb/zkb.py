import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier


class ZurcherKantonalBank(BankBase):
    name = "zkb"

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"Balance as of: ({ISO8601.DD_MM_YYYY})"),
        header_pattern=re.compile(r"(Date.*Booking text.*Debit CHF.*Credit CHF)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MM_YYYY})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?P<amount>\d{1,3}(\'\d{3})*(\.\d+)?)\s+"
            + rf"(?P<value_date>{ISO8601.DD_MM_YYYY})\s+"
            + r"(?P<balance>\d{1,3}(\'\d{3})*(\.\d+)?)$"
        ),
        multiline_config=MultilineConfig(multiline_descriptions=True),
        safety_check=False,
        transaction_date_format="%d.%m.%Y",
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
