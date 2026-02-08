import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import EntryType
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier


class CanadianTire(BankBase):
    name = "canadian_tire"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"\s+DATE\s+DATE\s+TRANSACTION\ DESCRIPTION\s+AMOUNT\ \(\$\)"),
        statement_date_pattern=re.compile(rf"Statement\s+date\s+(?P<statement_date>{ISO8601.MMMM_DD_YYYY})"),
        transaction_pattern=re.compile(
            r"^\s*"
            r"(?P<transaction_date>[A-Z][a-z]{2}\s\d{2})\s+"
            r"(?P<posting_date>[A-Z][a-z]{2}\s\d{2})\s+"
            r"(?!\s*\d+\b)"
            r"(?P<description>.+?)\s{2,}"  # NOTE: no way to not parse trailing text in line as description?
            r"(?P<polarity>-)"
            r"?(?P<amount>\d{1,3}(?:,\d{3})*\.\d{2})"
        ),
        transaction_date_format="%b %d",
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    identifiers = [[MetadataIdentifier(author="Canadian Tire Bank / Banque Canadian Tire", producer="PDFlib+PDI")]]

    statement_configs = [credit]
