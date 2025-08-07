import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants.date import ISO8601, DateFormats
from monopoly.constants.statement import (
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    SharedPatterns,
)
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Scotiabank(BankBase):
    name = BankNames.SCOTIABANK

    debit_personal = StatementConfig(
        statement_type=EntryType.DEBIT,
        header_pattern=re.compile(r"\s+Date\s+Transactions\s+withdrawn\ \(\$\)\s+deposited\ \(\$\)\s+Balance\ \(\$\)"),
        statement_date_pattern=re.compile(
            rf"Closing Balance on (?P<date>{DateFormats.MMMM}\s+{DateFormats.DD},\s+{DateFormats.YYYY})"
        ),
        transaction_date_format="%b %d",
        transaction_pattern=DebitTransactionPatterns.SCOTIABANK,
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )
    debit_business = StatementConfig(
        statement_type=EntryType.DEBIT,
        header_pattern=re.compile(
            r"(\s+)?Date\s+Description\s+Withdrawals/Debits \(\$\)\s+Deposits/Credits \(\$\)\s+Balance \(\$\)"
        ),
        statement_date_pattern=re.compile(
            r"(?P<last_date>\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{4}\b)(?!.*\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{4}\b)"
        ),
        transaction_date_format="%m/%d/%Y",
        transaction_pattern=re.compile(
            r"^(?!.*(?:BALANCE FORWARD)).*?"
            rf"(?P<transaction_date>{DateFormats.MM}\/{DateFormats.DD}\/{DateFormats.YYYY})\s+"
            + SharedPatterns.DESCRIPTION
            # cents (float) are optional in bank statement. "\.\d*" -> "(?:\.\d{1,2})?"
            + r"(?P<amount>\(?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})??\)?)\s+"
            + r"(?P<balance>\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)"
        ),
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    credit_variant_1 = StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"\s+REF\.\#\ DATE\s+DATE\s+DETAILS\s+AMOUNT\(\$\)"),
        prev_balance_pattern=re.compile(
            rf"Previous balance,\s+{ISO8601.MMM_DD}\/"
            r"\d{2,}\s+"
            rf"(?P<balance>${SharedPatterns.COMMA_FORMAT})"
        ),
        statement_date_pattern=re.compile(
            # r"Jun 24, 2025 - Jul 23, 2025"
            rf"- {ISO8601.MMM_DD_YYYY}"
        ),
        transaction_date_format="%b %d",
        transaction_pattern=CreditTransactionPatterns.SCOTIABANK,
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    identifiers = [
        # DR personal
        [
            MetadataIdentifier(
                producer="CrawfordTech PDF Driver Version 5.1 64 Bit Build ID 7361 on March 09, 2022 at 20:00:30"
            ),
            TextIdentifier(text="www.scotiabank.com"),
        ],
        # DR business
        [
            MetadataIdentifier(
                creator="BIRT Report Engine 2.5.1 using iText 1.5.4.",
                producer=(
                    "iText 1.5.2 (release for Eclipse/BIRT by lowagie.com); "
                    "modified using iText® 5.5.13.1 ©2000-2019 iText Group NV (AGPL-version)"
                ),
            ),
        ],
        # CR
        [
            MetadataIdentifier(
                producer="CrawfordTech PDF Driver Version 5.1 64 Bit Build ID 7361 on March 09, 2022 at 20:00:30"
            ),
            TextIdentifier(text="\nScotiabank"),
            TextIdentifier(text="Scotia\nCredit\nCard"),
        ],
    ]
    statement_configs = [debit_personal, debit_business, credit_variant_1]
