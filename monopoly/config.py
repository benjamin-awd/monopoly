from typing import Annotated

from pydantic import ConfigDict, StringConstraints
from pydantic.dataclasses import dataclass
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
    static_string: str = None
    brute_force_mask: str = None
    password: str = None
    page_range: tuple = (None, None)
    page_bbox: tuple = None


settings = Settings()

arbitrary_config = ConfigDict(arbitrary_types_allowed=True)
