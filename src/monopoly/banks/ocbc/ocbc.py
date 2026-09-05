import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PaymentSummaryConfig, PdfConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Ocbc(BankBase):
    name = "ocbc"

    credit = StatementConfig(
        currency="SGD",
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MM_YYYY.regex,
        # 16-digit card number, e.g. "1234-5678-9012-2605" (next to the cardholder
        # name and again on the summary row). A consolidated statement lists several
        # cards; the first match (primary card) is stamped on all rows.
        account_pattern=re.compile(r"\b(?P<account>\d{4}-\d{4}-\d{4}-\d{4})\b"),
        header_pattern=re.compile(r"(TRANSACTION DATE.*DESCRIPTION.*AMOUNT)"),
        prev_balance_pattern=re.compile(
            r"(?P<description>LAST MONTH'S BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=re.compile(
            r"(?P<transaction_date>\d+/\d+)\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
        ),
        transaction_date_format="%d/%m",
        payment_summary_config=PaymentSummaryConfig(
            # payment slip near the foot of page 1: "PAYMENT DUE DATE : 24 AUG 23"
            payment_due_date=re.compile(r"PAYMENT DUE DATE\s*:\s*(?P<due_date>\d{1,2}\s+\w{3}\s+\d{2,4})"),
            total_amount_due=re.compile(r"TOTAL AMOUNT DUE\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL),
            # last S$ figure on the summary row: "01-08-2023  24-08-2023  S$22,800  S$22,058.11  S$50.00"
            minimum_payment=re.compile(r"\d{2}-\d{2}-\d{4}\s+\d{2}-\d{2}-\d{4}.*S\$\s*(?P<amount>[\d,]+\.\d{2})"),
        ),
    )

    debit = StatementConfig(
        currency="SGD",
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"\s{ISO8601.DD_MMM_YYYY}$"),
        # statement period line, e.g. "01 SEP 2024 TO 30 SEP 2024" (start is period end - 1 cycle)
        period_start_pattern=re.compile(r"(?i)(\d{1,2} \w{3} \d{4})\s+TO\s+\d{1,2} \w{3} \d{4}"),
        # account number in the header block, e.g. "Account No. 987654321098"
        account_pattern=re.compile(r"(?i)Account No\.?\s+(?P<account>\d{6,})"),
        header_pattern=re.compile(r"(Withdrawal.*Deposit.*Balance)"),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
            + SharedPatterns.BALANCE
        ),
        multiline_config=MultilineConfig(multiline_descriptions=True),
        transaction_bound=170,
        transaction_date_format="%d %b",
    )

    pdf_config = PdfConfig(
        remove_vertical_text=True,
    )

    identifiers = [
        [
            MetadataIdentifier(creator="pdfgen", producer="Streamline PDFGen for OCBC Group"),
            TextIdentifier("OCBC"),
        ],
    ]

    statement_configs = [credit, debit]
