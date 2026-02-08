import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PdfConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Ocbc(BankBase):
    name = "ocbc"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MM_YYYY,
        header_pattern=re.compile(r"(TRANSACTION DATE.*DESCRIPTION.*AMOUNT)"),
        prev_balance_pattern=re.compile(
            r"(?P<description>LAST MONTH'S BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=re.compile(
            r"(?P<transaction_date>\d+/\d+)\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
        ),
        transaction_date_format="%d/%m",
    )

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"\s{ISO8601.DD_MMM_YYYY}$"),
        header_pattern=re.compile(r"(Withdrawal.*Deposit.*Balance)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
            + SharedPatterns.BALANCE
        ),
        multiline_config=MultilineConfig(multiline_descriptions=True),
        transaction_bound=170,
        transaction_date_format="%d %b",
    )

    pdf_config = PdfConfig(
        remove_vertical_text=True,
    )

    identifiers = [
        [
            MetadataIdentifier(creator="pdfgen", producer="Streamline PDFGen for OCBC Group"),
            TextIdentifier("OCBC"),
        ],
    ]

    statement_configs = [credit, debit]
