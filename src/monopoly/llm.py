"""Shared configuration for Gemini-backed LLM features (extraction and OCR)."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MissingApiKeyError(Exception):
    """Raised when a required API key is not configured."""


class GeminiSettings(BaseSettings):
    google_api_key: SecretStr | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
