from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gcs_bucket: str
    gmail_address: str
    project_id: str
    pubsub_topic: str
    secret_id: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
