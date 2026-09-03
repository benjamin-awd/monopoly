import re

from monopoly.banks.base import BankBase
from monopoly.config import PaymentSummaryConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class StandardChartered(BankBase):
    name = "standard_chartered"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf": {ISO8601.DD_MMM_YYYY}$"),
        header_pattern=re.compile(r"(Transaction.*Posting.*Amount)"),
        prev_balance_pattern=re.compile(
            r"(?P<description>BALANCE FROM PREVIOUS STATEMENT?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
            + SharedPatterns.DESCRIPTION
            + r"(?:(?P<transaction_ref>Transaction\sRef\s\d+)?)\s+"
            + SharedPatterns.AMOUNT_EXTENDED
        ),
        transaction_date_format="%d %b",
        payment_summary_config=PaymentSummaryConfig(
            payment_due_date=re.compile(r"Payment Due Date\s*:\s*(?P<due_date>\d{1,2}\s+\w{3}\s+\d{4})"),
            # uppercase labels on the summary page (distinct from the "New Balance" column header)
            total_amount_due=re.compile(r"NEW BALANCE\s+(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"),
            minimum_payment=re.compile(r"MINIMUM PAYMENT DUE\s+(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"),
        ),
    )

    identifiers = [
        [
            MetadataIdentifier(
                title="eStatement",
                producer="iText",
            ),
            TextIdentifier("Standard Chartered"),
        ]
    ]

    statement_configs = [credit]
