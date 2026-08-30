import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PaymentSummaryConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Dbs(BankBase):
    name = "dbs"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MMM_YYYY,
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        transaction_date_format="%d %b",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
        ),
        prev_balance_pattern=re.compile(
            r"(?P<description>PREVIOUS BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        payment_summary_config=PaymentSummaryConfig(
            # top summary row: "15 Oct 2023   $25,000.00   $509.08   09 Nov 2023"
            #                  (statement date, credit limit, min payment, due date)
            payment_due_date=re.compile(
                r"\d{1,2}\s+\w{3}\s+\d{4}\s+\$[\d,]+\.\d{2}\s+\$[\d,]+\.\d{2}\s+"
                r"(?P<due_date>\d{1,2}\s+\w{3}\s+\d{4})"
            ),
            # payment coupon: "TOTAL   $ 16,969.17   $ 509.08"
            total_amount_due=re.compile(
                r"TOTAL\s+\$\s*(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")\s+\$\s*[\d,]+\.\d{2}"
            ),
            minimum_payment=re.compile(
                r"TOTAL\s+\$\s*[\d,]+\.\d{2}\s+\$\s*(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"
            ),
        ),
    )

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=ISO8601.DD_MMM_YYYY,
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            description_margin=10,  # Allow for indented PayNow/transaction details
        ),
        header_pattern=re.compile(r"(WITHDRAWAL.*DEPOSIT.*BALANCE)"),
        transaction_date_format="%d %b",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_bound=170,
    )

    consolidated = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"Details as at {ISO8601.DD_MMM_YYYY}"),
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            description_margin=10,  # Allow for indented PayNow/transaction details
        ),
        header_pattern=re.compile(r"(\s*Date\s+Description\s+Withdrawal.*)"),
        transaction_date_format="%d/%m/%Y",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MM_YYYY})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_bound=220,
    )

    identifiers = [
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="Quadient CXM AG"),
        ],
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="Quadient"),
        ],
    ]

    statement_configs = [credit, consolidated, debit]
