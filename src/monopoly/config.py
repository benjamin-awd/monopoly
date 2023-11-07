from typing import Annotated, Optional

from pydantic import StringConstraints
from pydantic.dataclasses import dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict

from monopoly.constants import AccountType, BankNames


class Settings(BaseSettings):
    """
    Pydantic model that automatically populates variables from a .env file.

    HSBC passwords differ per card (since HSBC uses the last 6 digits of each card).
    If only a single statement from HSBC needs to be parsed, the hsbc_pdf_password
    can be used.

    If there are multiple statements from HSBC, the `hsbc_pdf_password_prefix` can
    be used to automatically unlock PDFs, which is used as a static string
    in the HSBC `brute_force_config`.
    """

    ocbc_pdf_password: str = ""
    citibank_pdf_password: str = ""
    standard_chartered_pdf_password: str = ""
    hsbc_pdf_password: str = ""
    hsbc_pdf_password_prefix: str = ""

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
    - `cashback_key` is the identifier that is used to differentiate cashback
    transactions from items we don't want to capture like AXS bill payments.
    e.g. if the cashback_key="CASH REBATE", we'll treat transactions containing
    "CASH REBATE" as cashback transactions, and include it in the statement
    - `multiline_transactions` controls whether Monopoly tries to concatenate
    transactions that are split across two lines
    """

    pattern: str
    date_format: Annotated[str, StringConstraints(pattern="%")]
    cashback_key: Optional[str] = None
    multiline_transactions: bool = False


@dataclass
class StatementConfig:
    """
    Stores configuration values for the `Statement` class
    """

    bank_name: BankNames
    account_type: AccountType
    statement_date_format: Annotated[str, StringConstraints(pattern="%.+%.+%")]
    statement_date_pattern: str

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

    password: Optional[str] = None
    page_range: tuple[Optional[int], Optional[int]] = (None, None)
    page_bbox: Optional[tuple[float, float, float, float]] = None


@dataclass
class BruteForceConfig:
    """
    Stores configuration values to help automatically unlock PDFs.

    Attributes:
    - `static_string`: A static string used in PDF passwords.

      Example: For a password format like "01Jan1999123456," the static string
      might be "01Jan1999," which remains constant across all HSBC statements
      for a particular user.

    - `mask`: A mask used for generating variations in the password.

      Example: In the same password format "01Jan1999123456," the mask
      represents the last six digits (e.g., "123456"). The masking pattern
      used in this case should be `?d?d?d?d?d?d`.

    These attributes are used together to automatically unlock PDFs where a portion
    of the password remains consistent (the static string) while another part varies
    (the brute force mask).
    """

    static_string: Optional[str] = None
    mask: Optional[str] = None


settings = Settings()
