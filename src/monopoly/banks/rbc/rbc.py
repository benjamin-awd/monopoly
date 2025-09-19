import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants.date import ISO8601, DateFormats
from monopoly.constants.statement import (
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class RoyalBankOfCanada(BankBase):
    name = BankNames.RBC

    debit_personal = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"From {ISO8601.MMMM_DD_YYYY} to (?P<date>{ISO8601.MMMM_DD_YYYY})"),
        header_pattern=re.compile(r"Date\s+Description\s+Withdrawals \(\$\)\s+Deposits \(\$\)\s+Balance\ \(\$\)"),
        transaction_pattern=DebitTransactionPatterns.RBC,
        transaction_date_format="%d %b",
        multiline_config=MultilineConfig(multiline_descriptions=True, multiline_transaction_date=True),
    )

    debit_business = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(
            rf"\b({DateFormats.MMMM}\s{DateFormats.D}[,\s]{{1,2}}{DateFormats.YYYY}) to "
            rf"(?P<date>\b({DateFormats.MMMM}\s{DateFormats.D}[,\s]{{1,2}}{DateFormats.YYYY}))"
        ),
        header_pattern=re.compile(
            r"Date\s+Description\s+Cheques\ \&\ Debits\ \(\$\)\s+Deposits\ \&\ Credits\ \(\$\)\s+Balance\ \(\$\)"
        ),
        transaction_pattern=re.compile(
            r"^(?!.*(?:Opening balance|Closing balance))"
            r"(\s+)?"
            rf"(?P<transaction_date>{DateFormats.DD}\s+{DateFormats.MMM})?"  # i.e 08 May
            r"\s+"
            r"(?P<description>.+?)"
            r"\s{2,}"
            r"(?P<amount>\d{1,3}(?:,\d{3})*(?:\.\d{1,2}))"
            r"(?:\s{2,}(?P<balance>-?\s?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})))?"
            r"\s*$"
        ),
        transaction_date_format="%d %b",
        multiline_config=MultilineConfig(multiline_descriptions=True, multiline_transaction_date=True),
    )

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(
            rf"STATEMENT FROM ({ISO8601.MMM_DD}|{ISO8601.MMM_DD_YYYY}) TO "
            rf"(({DateFormats.MMM}\s{DateFormats.D}[,\s]{{1,2}}{DateFormats.YYYY})|{ISO8601.MMM_DD_YYYY})"
        ),
        header_pattern=re.compile(r"(TRANSACTION\s+POSTING)"),
        prev_balance_pattern=StatementBalancePatterns.RBC,
        transaction_pattern=CreditTransactionPatterns.RBC,
        transaction_date_format="%b %d",
    )

    identifiers = [
        # DR personal
        [
            MetadataIdentifier(creator="Symcor Inc.", producer="PDFlib+PDI"),
            TextIdentifier(text="Royal Bank of Canada"),
        ],
        [
            MetadataIdentifier(creator="Symcor Inc.", producer="PDFlib+PDI", title="Statement"),
            TextIdentifier(text="Royal Bank of Canada"),
        ],
        # DR business
        [
            MetadataIdentifier(creator="Symcor Inc.", producer="PDFlib+PDI"),
            TextIdentifier(text="ROYAL BANK OF CANADA"),
        ],
        [
            MetadataIdentifier(creator="Symcor Inc.", producer="PDFlib+PDI", title="Statement"),
            TextIdentifier(text="ROYAL BANK OF CANADA"),
        ],
        # CR
        [
            MetadataIdentifier(creator="Symcor Inc.", producer="PDFlib+PDI"),
            TextIdentifier(text="RBC ROYAL BANK"),
        ],
    ]
    statement_configs = [debit_personal, debit_business, credit]
