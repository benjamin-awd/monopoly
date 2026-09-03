from collections.abc import Sequence
from dataclasses import dataclass, field
from re import Pattern

from monopoly.constants import EntryType
from monopoly.enums import RegexEnum
from monopoly.identifiers import IdentifierGroup


@dataclass
class DateOrder:
    """
    Store for date order argument to date parser.

    Supported `dateparser` DATE_ORDER arguments can be found here:
    https://dateparser.readthedocs.io/en/latest/settings.html#date-order.
    """

    date_order: str

    @property
    def settings(self):
        return {"DATE_ORDER": self.date_order}


@dataclass
class MultilineConfig:
    multiline_descriptions: bool = False
    multiline_polarity: bool = False
    multiline_statement_date: bool = False
    multiline_transaction_date: bool = False
    include_prev_margin: int | None = None
    description_margin: int = 3


@dataclass
class PaymentSummaryConfig:
    r"""
    Regex patterns for extracting a credit statement's payment summary.

    The payment summary is the block of figures on a credit card statement that
    states what the cardholder must pay, and by when (as opposed to the
    individual transactions). Each pattern is optional; a bank only needs to
    configure the fields it can reliably locate.

    - `payment_due_date` should expose a named `due_date` group, e.g.
        r"PAYMENT DUE DATE\s*:\s*(?P<due_date>\d{2} \w{3} \d{2})"
    - `total_amount_due` and `minimum_payment` should each expose a named
    `amount` group, e.g. r"TOTAL AMOUNT DUE\s+(?P<amount>[\d,]+\.\d{2})".
    """

    payment_due_date: Pattern[str] | RegexEnum | None = None
    total_amount_due: Pattern[str] | RegexEnum | None = None
    minimum_payment: Pattern[str] | RegexEnum | None = None


# pylint: disable=too-many-instance-attributes
@dataclass(kw_only=True)
class StatementConfig:
    r"""
    Configuration store for statements that are dynamically generated at runtime.

    Base configuration class storing configuration values for debit and
    credit card statements.

    - `transaction_pattern` refers to the regex pattern used to capture transactions,
    where a pattern like:
        "(?P<transaction_date>\\d+/\\d+)\\s*"
        "(?P<description>.*?)\\s*"
        "(?P<amount>[\\d.,]+)$"
    is used to capture a transaction like:
        06/07 URBAN TRANSIT CO. SINGAPORE SG  1.38
    - `transaction_date_order` represents the datetime format that a specific bank uses
    for transactions. For example, "DMY" will parse 01/02/2024 as 1 Feb 2024.
    Defaults to DMY.
    - `statement_date_format` represents the datetime format that a specific bank uses
    to represent a statement date.
    - `multiline_config` determines whether Monopoly tries to concatenate
    transactions that are split across two lines
    - `header_pattern` is a regex pattern that is used to find the 'header' line
    of a statement, and determine if it is a debit or credit card statement.
    - `transaction_bound` will cause transactions that have an amount past a certain
    number of spaces will be ignored. For example, if `transaction_bound` = 32:
        "01 NOV  BALANCE B/F              190.77" (will be ignored)
        "01 NOV  YA KUN KAYA TOAST  12.00       " (will be kept)
    - `transaction_auto_polarity` controls whether transaction amounts are set as negative.
    or positive if they have 'CR' or '+' as a polarity identifier. Enabled by default.
    If enabled, only 'CR' or '+' will make a transaction positive. Disabled by default.
    - `safety_check` controls whether the safety check for banks. Use
    for banks that don't provide total amount (or total debit/credit)
    in the statement. Enabled by default.
    - `filename_fallback_pattern` is an optional regex pattern that extracts the statement
    date from the filename when it cannot be found in the PDF content. The pattern should
    have two capture groups: (1) month abbreviation and (2) year (e.g., r"_([A-Za-z]{3})(\d{4})")
    to match filenames like "eStatement_Nov2025_*.pdf". Disabled by default (None).
    - `payment_summary_config` is an optional `PaymentSummaryConfig` holding the regex
    patterns used to extract the credit statement's payment summary (payment due date,
    total amount due, minimum payment). See `CreditStatement.payment_summary`. Disabled by
    default (None).
    """

    statement_type: EntryType
    transaction_pattern: Pattern[str] | RegexEnum
    statement_date_pattern: Pattern[str] | RegexEnum
    header_pattern: Pattern[str] | RegexEnum
    transaction_date_order: DateOrder = field(default_factory=lambda: DateOrder("DMY"))
    statement_date_order: DateOrder = field(default_factory=lambda: DateOrder("DMY"))
    transaction_date_format: str = ""
    multiline_config: MultilineConfig = field(default_factory=MultilineConfig)
    transaction_bound: int | None = None
    prev_balance_pattern: Pattern[str] | RegexEnum | None = None
    safety_check: bool = True
    transaction_auto_polarity: bool = True
    filename_fallback_pattern: Pattern[str] | None = None
    payment_summary_config: PaymentSummaryConfig | None = None


@dataclass
class PdfConfig:
    """
    Stores PDF configuration values for the `PdfParser` class.

    - `page_range`: A slice representing which pages to process. For
    example, a range of (1, -1) will mean that the first and last pages
    are skipped.
    - `page_bbox`: A tuple representing the bounding box range for every
    page. This is used to avoid weirdness like vertical text, and other
    PDF artifacts that may affect parsing.
    - `ocr_identifiers`: Applies OCR on PDFs with a specific metadata identifier.
    - `remove_vertical_text`: Whether to remove vertical text from the PDF. This
    helps to avoid issues with pdftotext's layout mode. For performance reasons,
    this defaults to False.
    """

    page_range: tuple[int | None, int | None] = (None, None)
    page_bbox: tuple[float, float, float, float] | None = None
    ocr_identifiers: Sequence[IdentifierGroup] | None = None
    remove_vertical_text: bool = False
