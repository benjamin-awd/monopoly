from typing import Annotated, Optional

from pydantic import StringConstraints
from pydantic.dataclasses import dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict

from monopoly.constants import AccountType, BankNames


class Settings(BaseSettings):
    """
    Pydantic model that automatically populates variables from a .env file.
    """

    ocbc_pdf_passwords: Optional[list[str]] = None
    citibank_pdf_passwords: Optional[list[str]] = None
    standard_chartered_pdf_passwords: Optional[list[str]] = None
    hsbc_pdf_passwords: Optional[list[str]] = None

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@dataclass
class TransactionConfig:
    """
    Stores configurations for transactions within the statement

    - `pattern` refers to the regex pattern used to capture transactions,
    where a pattern like:
        "(?P<transaction_date>\\d+/\\d+)\\s*"
        "(?P<description>.*?)\\s*"
        "(?P<amount>[\\d.,]+)$"
    is used to capture a transaction like:
        06/07 URBAN TRANSIT CO. SINGAPORE SG  1.38
    - `date_format` represents the datetime format that a specific bank uses
    for transactions. For example, "%d/%m" will match 06/07
    - `multiline_transactions` controls whether Monopoly tries to concatenate
    transactions that are split across two lines
    """

    pattern: str
    date_format: Annotated[str, StringConstraints(pattern="%")]
    multiline_transactions: bool = False


@dataclass
class StatementConfig:
    """
    Stores configuration values for the `Statement` class
    """

    bank_name: BankNames
    account_type: AccountType
    date_format: Annotated[str, StringConstraints(pattern="%.+%.+%")]
    date_pattern: str
    prev_balance_pattern: str

    # Convert enums to strings
    def __post_init__(self):
        self.bank_name = self.bank_name.value
        self.account_type = self.account_type.value


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

    passwords: Optional[list[str]] = None
    page_range: tuple[Optional[int], Optional[int]] = (None, None)
    page_bbox: Optional[tuple[float, float, float, float]] = None


settings = Settings()
