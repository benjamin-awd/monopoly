from typing import Annotated

from pydantic import ConfigDict, StringConstraints
from pydantic.dataclasses import Field, dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict

from monopoly.constants import AccountType, BankNames


class Settings(BaseSettings):
    gmail_address: str = ""
    project_id: str = ""
    pubsub_topic: str = ""
    secret_id: str = ""
    gcs_bucket: str = ""
    ocbc_pdf_password: str = ""
    citibank_pdf_password: str = ""
    hsbc_pdf_password_prefix: str = ""
    trusted_user_emails: list = []

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

    Attributes:
    - `static_string` and `brute_force` mask are used together to unlock
    PDF. For example, HSBC has a password format like 01Jan1999123456,
    where 01Jan1999 is a static string that never changes, and
    123456 reflects that last six digits of a credit card, which will
    not be consistent across different credit card statements.
    - `password`: The password used to unlock the PDF (if it is locked)
    - `page_range`: A slice representing which pages to process. For
    example, a range of (1, -1) will mean that the first and last pages
    are skipped.
    - `page_bbox`: A tuple representing the bounding box range for every
    page. This is used to avoid weirdness like vertical text, and other
    PDF artifacts that may affect parsing.
    - `psm`: Page segmentation mode for Tesseract. Defaults to 6, which
    which is: "assume a single uniform block of text"
    """

    static_string: str = None
    brute_force_mask: str = None
    password: str = None
    page_range: tuple = (None, None)
    page_bbox: tuple = None
    psm: int = Field(6, ge=0, le=13)


settings = Settings()

arbitrary_config = ConfigDict(arbitrary_types_allowed=True)
