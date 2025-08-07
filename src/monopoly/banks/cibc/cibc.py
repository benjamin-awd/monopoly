import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import (
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.constants.date import DateFormats
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class CIBC(BankBase):
    name = BankNames.CIBC

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        header_pattern=re.compile(
            r"(\s+)?Date\s+Description\s+Withdrawals\ \(\$\)\s+Deposits\ \(\$\)\s+Balance\ \(\$\)"
        ),
        statement_date_pattern=re.compile(
            rf"(?:to\s+)?(?P<date>{DateFormats.MMM}\s+{DateFormats.DD},\s+{DateFormats.YYYY})"
        ),
        transaction_pattern=DebitTransactionPatterns.CIBC,
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
        prev_balance_pattern=StatementBalancePatterns.CIBC,
        transaction_pattern=CreditTransactionPatterns.CIBC,
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
