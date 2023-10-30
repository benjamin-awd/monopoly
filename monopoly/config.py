from typing import Annotated, Optional

from pydantic import ConfigDict, StringConstraints
from pydantic.dataclasses import dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict

from monopoly.constants import AccountType, BankNames


class Settings(BaseSettings):
    ocbc_pdf_password: str = ""
    citibank_pdf_password: str = ""
    standard_chartered_pdf_password: str = ""
    hsbc_pdf_password_prefix: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@dataclass
class StatementConfig:
    bank_name: BankNames
    account_type: AccountType
    statement_date_format: Annotated[str, StringConstraints(pattern="%.+%.+%")]
    transaction_pattern: str
    transaction_date_format: Annotated[str, StringConstraints(pattern="%")]
    statement_date_pattern: str
    multiline_transactions: bool = False

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

arbitrary_config = ConfigDict(arbitrary_types_allowed=True)
