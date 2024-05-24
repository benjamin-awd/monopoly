import re
from typing import Any, Optional

from pydantic import ConfigDict, SecretStr
from pydantic.dataclasses import dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict

from monopoly.constants import BankNames


class PdfPasswords(BaseSettings):
    ocbc_pdf_passwords: list[SecretStr] = [SecretStr("")]
    citibank_pdf_passwords: list[SecretStr] = [SecretStr("")]
    standard_chartered_pdf_passwords: list[SecretStr] = [SecretStr("")]
    hsbc_pdf_passwords: list[SecretStr] = [SecretStr("")]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


class Passwords(BaseSettings):
    """
    Pydantic model that automatically populates variables from a .env file,
    or an environment variable called `passwords`.
    e.g. export PASSWORDS='{"OCBC_PDF_PASSWORDS": ...}'
    """

    passwords: PdfPasswords = PdfPasswords()


# pylint: disable=too-many-instance-attributes
@dataclass(kw_only=True)
class StatementConfig:
    """
    Base configuration class storing configuration values for debit and
    credit card statements

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
    - `multiline_transactions` controls whether Monopoly tries to concatenate
    transactions that are split across two lines
    - `debit_statement_identifier` is a regex pattern that is used to determine whether
    a statement from a bank is a debit or credit card statement.
    """

    bank_name: BankNames
    transaction_pattern: str
    statement_date_pattern: str
    transaction_date_order: dict[str, str] = "DMY"
    statement_date_order: dict[str, str] = "DMY"
    multiline_transactions: bool = False

    def wrap_date_order_in_dict(self):
        if self.statement_date_order:
            self.statement_date_order = {"DATE_ORDER": self.statement_date_order}

        if self.transaction_date_order:
            self.transaction_date_order = {"DATE_ORDER": self.transaction_date_order}


@dataclass(config=ConfigDict(extra="forbid"), kw_only=True)
class DebitStatementConfig(StatementConfig):
    """
    Dataclass storing configuration values unique to debit statements
    """

    debit_statement_identifier: str

    def __post_init__(self):
        self.wrap_date_order_in_dict()


@dataclass(config=ConfigDict(extra="forbid"))
class CreditStatementConfig(StatementConfig):
    """
    Dataclass storing configuration values unique to credit statements

    - `prev_balance_pattern` is a regex pattern used to match the previous balance
    line in a credit statements, which is then treated as a transaction.
    """

    prev_balance_pattern: Optional[Any | re.Pattern] = None

    def __post_init__(self):
        if self.prev_balance_pattern:
            self.prev_balance_pattern = re.compile(self.prev_balance_pattern)

        self.wrap_date_order_in_dict()


@dataclass
class PdfConfig:
    """Stores PDF configuration values for the `PdfParser` class

    - `password`: The password used to unlock the PDF (if it is locked)
    - `page_range`: A slice representing which pages to process. For
    example, a range of (1, -1) will mean that the first and last pages
    are skipped.
    - `page_bbox`: A tuple representing the bounding box range for every
    page. This is used to avoid weirdness like vertical text, and other
    PDF artifacts that may affect parsing.
    """

    page_range: tuple[Optional[int], Optional[int]] = (None, None)
    page_bbox: Optional[tuple[float, float, float, float]] = None


passwords = Passwords().passwords
