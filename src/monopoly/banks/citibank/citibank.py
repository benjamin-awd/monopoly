import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, PdfConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Citibank(BankBase):
    name = "citibank"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(r"Statement\sDate\s+(.*)"),
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        transaction_date_format="%d %b",
        prev_balance_pattern=re.compile(
            r"(?P<description>BALANCE PREVIOUS STATEMENT?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
        ),
        filename_fallback_pattern=re.compile(r"_([A-Za-z]{3})(\d{4})"),
    )

    credit_us = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(
            r"Billing Period:\s+\d{2}/\d{2}/\d{2}-(\d{2}/\d{2}/\d{2})"
        ),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(date\s+date\s+Description\s+Amount)", re.IGNORECASE),
        transaction_date_format="%m/%d",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
            rf"(?:(?P<posting_date>{ISO8601.MM_DD})\s+)?"
            + SharedPatterns.DESCRIPTION
            + r"(?P<polarity>\-)?"
            + r"\$(?P<amount>"
            + SharedPatterns.COMMA_FORMAT
            + r")"
        ),
    )

    pdf_config = PdfConfig(
        remove_vertical_text=True,
    )

    identifiers = [
        [
            MetadataIdentifier(
                creator="Ricoh Americas Corporation, AFP2PDF",
                producer="Ricoh Americas Corporation, AFP2PDF",
            )
        ],
        [
            MetadataIdentifier(author="Citibank, N.A."),
            TextIdentifier("citicards.com"),
        ],
    ]

    statement_configs = [credit, credit_us]
