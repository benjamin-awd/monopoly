import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import EntryType
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

# Indian (lakh) digit grouping: 1,23,456.78
AMOUNT = r"\d{1,3}(?:,\d{2,3})*\.\d{2}"


class Hdfc(BankBase):
    name = "hdfc"

    # Layout in use since about Aug 2025. pdftotext renders the rupee glyph as
    # "C" and the purchase-indicator bullet that ends each row as "l".
    credit = StatementConfig(
        currency="INR",
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(r"Statement Date\s+(\d{2} \w{3}, \d{4})"),
        period_start_pattern=re.compile(r"Billing Period\s+(\d{2} \w{3}, \d{4})\s+-"),
        account_pattern=re.compile(r"Credit Card No\.\s+(?P<account>[\dX]{16})"),
        header_pattern=re.compile(r"DATE & TIME\s+TRANSACTION DESCRIPTION"),
        transaction_pattern=re.compile(
            # date and time; international rows put a space before the pipe
            r"(?P<transaction_date>\d{2}/\d{2}/\d{4})\s?\|\s*\d{2}:\d{2}\s+"
            r"(?:EMI\s+)?"
            r"(?P<description>.*?)\s*"
            # reward points, e.g. "+ 30" or "+5": always has digits
            r"(?:[+-]\s?\d+\s+)?"
            # a credit is a bare "+" directly before the rupee glyph
            r"(?P<direction>\+)?\s*"
            rf"C\s?(?P<amount>{AMOUNT})"
            r"\s*(?:l\s*)?$"
        ),
        transaction_date_format="%d/%m/%Y",
        # fee and tax rows print their description on the lines above and below
        multiline_config=MultilineConfig(straddled_descriptions=True),
    )

    identifiers = [
        [
            TextIdentifier("HDFC Bank Credit Cards"),
            MetadataIdentifier(creator="Quadient~Inspire"),
        ],
    ]

    statement_configs = [credit]
