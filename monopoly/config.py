from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


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


settings = Settings()

arbitrary_config = ConfigDict(arbitrary_types_allowed=True)
