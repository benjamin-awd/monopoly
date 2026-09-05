import re

from monopoly.banks.base import BankBase
from monopoly.config import DateOrder, PaymentSummaryConfig, PdfConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Citibank(BankBase):
    name = "citibank"

    credit = StatementConfig(
        currency="SGD",
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
        payment_summary_config=PaymentSummaryConfig(
            # summary block: "Payment Due Date   March 12, 2022"
            payment_due_date=re.compile(r"Payment Due Date\s*:?\s*(?P<due_date>[A-Z][a-z]+ \d{1,2}, \d{4})"),
            # Citibank bills the full current balance: "Current Balance   $1,060.88"
            total_amount_due=re.compile(r"Current Balance\s+\$\s*(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"),
            minimum_payment=re.compile(
                r"Total Minimum Payment\s+\$\s*(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"
            ),
        ),
    )

    credit_us = StatementConfig(
        currency="USD",
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(r"Billing Period:\s+\d{2}/\d{2}/\d{2}-(\d{2}/\d{2}/\d{2})"),
        statement_date_order=DateOrder("MDY"),
        transaction_date_order=DateOrder("MDY"),
        header_pattern=re.compile(r"(date\s+date\s+Description\s+Amount)", re.IGNORECASE),
        transaction_date_format="%m/%d",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
            rf"(?:(?P<posting_date>{ISO8601.MM_DD})\s+)?"
            + SharedPatterns.DESCRIPTION
            + r"(?P<direction>\-)?"
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
