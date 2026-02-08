import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import DateFormats
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class CIBC(BankBase):
    name = "cibc"

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        header_pattern=re.compile(
            r"(\s+)?Date\s+Description\s+Withdrawals\ \(\$\)\s+Deposits\ \(\$\)\s+Balance\ \(\$\)"
        ),
        statement_date_pattern=re.compile(
            rf"(?:to\s+)?(?P<date>{DateFormats.MMM}\s+{DateFormats.DD},\s+{DateFormats.YYYY})"
        ),
        transaction_pattern=re.compile(
            rf"\s*(?:(?P<transaction_date>{DateFormats.MMM}\s+{DateFormats.D})[-\s]+)?"
            r"(?P<description>(?!(Deposits)).+?)\s{2,}"
            rf"(?P<amount>{SharedPatterns.COMMA_FORMAT})"
            rf"[-\s]+(?P<balance>{SharedPatterns.OPTIONAL_NEGATIVE_SYMBOL}\$?{SharedPatterns.COMMA_FORMAT})"
        ),
        transaction_date_format="%b %d",
        transaction_date_order=DateOrder("DMY"),
        statement_date_order=DateOrder("DMY"),
        multiline_config=MultilineConfig(
            multiline_transaction_date=True,
            multiline_descriptions=True,
        ),
        safety_check=True,
        transaction_auto_polarity=True,
    )

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(
            rf"(?:to\s+)?(?P<date>{DateFormats.MMM}\s+{DateFormats.DD},\s+{DateFormats.YYYY})"
        ),
        header_pattern=re.compile(r"\s+date\s+date\s+Description\s+Spend Categories\s+Amount\(\$\)"),
        prev_balance_pattern=re.compile(
            r"(?P<description>Previous balance?)\s+"
            rf"(?P<amount>{SharedPatterns.OPTIONAL_NEGATIVE_SYMBOL}\$?{SharedPatterns.COMMA_FORMAT})"
        ),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>\b({DateFormats.MMM}[-\s]{DateFormats.DD}))\s+"
            rf"(?P<posting_date>\b({DateFormats.MMM}[-\s]{DateFormats.DD}))\s+"
            r"(?:Ý\s*)?(?P<description>.+?)\s{2,}"
            r"(?P<catagory>.*?)\s+"
            # transaction dr/cr with format -$999,000.00
            rf"(?P<amount>{SharedPatterns.OPTIONAL_NEGATIVE_SYMBOL}\$?{SharedPatterns.COMMA_FORMAT}|{SharedPatterns.ENCLOSED_COMMA_FORMAT}\s*"
        ),
        transaction_date_format="%b %d",
        transaction_auto_polarity=False,
    )

    identifiers = [
        [
            TextIdentifier(text="CIBC Account Statement"),
            MetadataIdentifier(producer="iText® 5.5.13.2 ©2000-2020 iText Group NV (AGPL-version)"),
        ],
        [
            MetadataIdentifier(
                author="CIBC", producer="Ricoh Americas Corporation, AFP2PDF Plus Version: 1.300.71, Linux"
            )
        ],
    ]

    statement_configs = [debit, credit]
