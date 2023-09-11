from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gmail_address: str = ""
    project_id: str = ""
    pubsub_topic: str = ""
    secret_id: str = ""
    gcs_bucket: str = ""
    ocbc_pdf_password: str = ""
    hsbc_pdf_password: str = ""
    trusted_user_emails: list = []

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
