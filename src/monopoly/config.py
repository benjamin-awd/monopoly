from typing import Annotated, Optional

from pydantic import SecretStr, StringConstraints
from pydantic.dataclasses import dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict

from monopoly.constants import BankNames


class PdfPasswords(BaseSettings):
    ocbc_pdf_passwords: list[SecretStr] = [SecretStr("")]
    citibank_pdf_passwords: list[SecretStr] = [SecretStr("")]
    standard_chartered_pdf_passwords: list[SecretStr] = [SecretStr("")]
    hsbc_pdf_passwords: list[SecretStr] = [SecretStr("")]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


class Settings(BaseSettings):
    """
    Pydantic model that automatically populates variables from a .env file,
    or an environment variable called `passwords`.
    e.g. export PASSWORDS='{"OCBC_PDF_PASSWORDS": ...}'
    """

    passwords: PdfPasswords = PdfPasswords()


# pylint: disable=too-many-instance-attributes
@dataclass
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
    - `transaction_date_format` represents the datetime format that a specific bank uses
    for transactions. For example, "%d/%m" will match 06/07
    - `multiline_transactions` controls whether Monopoly tries to concatenate
    transactions that are split across two lines
    - `debit_statement_identifier` is a regex pattern that is used to determine whether
    a statement from a bank is a debit or credit card statement.
    """

    bank_name: BankNames
    transaction_pattern: str
    transaction_date_format: Annotated[str, StringConstraints(pattern="%")]
    statement_date_pattern: str
    statement_date_format: Annotated[str, StringConstraints(pattern="%.+%.+%")]
    multiline_transactions: bool = False
    debit_statement_identifier: Optional[str] = None


@dataclass
class DebitStatementConfig(StatementConfig):
    """
    Dataclass storing configuration values unique to debit statements
    """


@dataclass
class CreditStatementConfig(StatementConfig):
    """
    Dataclass storing configuration values unique to credit statements

    - `prev_balance_pattern` is a regex pattern used to match the previous balance
    line in a credit statements, which is then treated as a transaction.
    """

    prev_balance_pattern: Optional[str] = None


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

    passwords: Optional[list[SecretStr]] = None
    page_range: tuple[Optional[int], Optional[int]] = (None, None)
    page_bbox: Optional[tuple[float, float, float, float]] = None


settings = Settings().passwords
