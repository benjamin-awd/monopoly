import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from re import Pattern
from typing import ClassVar

from monopoly.constants import EntryType
from monopoly.enums import RegexEnum
from monopoly.identifiers import IdentifierGroup


def compile_pattern(value: "Pattern[str] | RegexEnum | str | None") -> "Pattern[str] | None":
    """
    Collapse any accepted spelling of a pattern to a compiled pattern.

    Config authors may write a compiled pattern, a `RegexEnum` member, or a
    bare regex string. Normalising here means every consumer downstream can
    assume `re.Pattern` and just call `.search()`, rather than each re-deriving
    the type with its own `isinstance` or `getattr` dance.
    """
    if value is None:
        return None
    if isinstance(value, RegexEnum):
        return value.regex
    if isinstance(value, str):
        return re.compile(value)
    if isinstance(value, Pattern):
        return value
    msg = f"Expected a compiled pattern, regex string or RegexEnum, got {type(value).__name__}: {value!r}"
    raise TypeError(msg)


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
    multiline_direction: bool = False
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

    payment_due_date: Pattern[str] | None = None
    total_amount_due: Pattern[str] | None = None
    minimum_payment: Pattern[str] | None = None

    PATTERN_FIELDS: ClassVar[tuple[str, ...]] = (
        "payment_due_date",
        "total_amount_due",
        "minimum_payment",
    )

    def __post_init__(self) -> None:
        for name in self.PATTERN_FIELDS:
            setattr(self, name, compile_pattern(getattr(self, name)))


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
    - `statement_date_pattern` locates the statement date, which is the *period end*
    surfaced as `period_end` in the JSON schema.
    - `period_start_pattern` is an optional regex that locates the statement's *period
    start* date, surfaced as the nullable `period_start` in the JSON schema. Parsed
    with the same date-order settings and named-group convention as
    `statement_date_pattern` (either a single capture group, or `day`/`month`/`year`
    groups). Content-only (no filename fallback); left None where unknown.
    - `account_pattern` is an optional regex that locates the statement's account or
    card number so its last 4 digits can be stamped onto every Transaction and
    surfaced as the nullable per-transaction `account` in the JSON schema (analogous
    to `currency`). It must expose a named `account` group capturing the account/card
    number token (masked digits like `4417 88XX XXXX 2031` are fine); the last 4
    digits are derived from it. Set per config/vintage, same shape as identifiers.
    Left None where unknown.
    - `multiline_config` determines whether Monopoly tries to concatenate
    transactions that are split across two lines
    - `header_pattern` is a regex pattern that is used to find the 'header' line
    of a statement, and determine if it is a debit or credit card statement.
    - `transaction_bound` will cause transactions that have an amount past a certain
    number of spaces will be ignored. For example, if `transaction_bound` = 32:
        "01 NOV  BALANCE B/F              190.77" (will be ignored)
        "01 NOV  YA KUN KAYA TOAST  12.00       " (will be kept)
    - `transaction_auto_direction` controls whether transaction amounts are set as negative.
    or positive if they have 'CR' or '+' as a direction identifier. Enabled by default.
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
    - `currency` is the ISO 4217 settlement currency this statement type is denominated
    in (what totals, balances and the safety check are in). It is stamped onto every
    Transaction in `Pipeline.extract` and surfaced in the JSON schema. Set per config
    (not per bank) so multi-country banks work: e.g. Maybank's MY configs are MYR while
    its SG config is SGD. Left None for the generic handler and where the currency is
    unknown. This is the account/settlement currency, distinct from a transaction's
    original/FX currency (a per-transaction follow-up).
    """

    statement_type: EntryType
    transaction_pattern: Pattern[str]
    statement_date_pattern: Pattern[str]
    header_pattern: Pattern[str]
    period_start_pattern: Pattern[str] | None = None
    account_pattern: Pattern[str] | None = None
    transaction_date_order: DateOrder = field(default_factory=lambda: DateOrder("DMY"))
    statement_date_order: DateOrder = field(default_factory=lambda: DateOrder("DMY"))
    transaction_date_format: str = ""
    multiline_config: MultilineConfig = field(default_factory=MultilineConfig)
    transaction_bound: int | None = None
    prev_balance_pattern: Pattern[str] | None = None
    safety_check: bool = True
    transaction_auto_direction: bool = True
    filename_fallback_pattern: Pattern[str] | None = None
    payment_summary_config: PaymentSummaryConfig | None = None

    PATTERN_FIELDS: ClassVar[tuple[str, ...]] = (
        "transaction_pattern",
        "statement_date_pattern",
        "header_pattern",
        "period_start_pattern",
        "account_pattern",
        "prev_balance_pattern",
        "filename_fallback_pattern",
    )

    def __post_init__(self) -> None:
        for name in self.PATTERN_FIELDS:
            setattr(self, name, compile_pattern(getattr(self, name)))

    currency: str | None = None


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
