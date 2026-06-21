import logging

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from monopoly.pdf import PdfDocument, PdfPage

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = (
    "Extract all text from this image exactly as it appears. "
    "Preserve the original layout, spacing, and line breaks. "
    "Do not add any commentary, headers, or formatting. "
    "Return only the raw text content."
)


class MissingApiKeyError(Exception):
    """Raised when a required API key is not configured."""


class GeminiSettings(BaseSettings):
    google_api_key: SecretStr | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


class GeminiOcr:
    def __init__(self, api_key: str | None = None):
        try:
            from google import genai
        except ImportError:
            msg = "google-genai is not installed. Install it with: pip install monopoly-core[gemini]"
            raise ImportError(msg) from None

        settings = GeminiSettings()
        key = api_key or (settings.google_api_key.get_secret_value() if settings.google_api_key else None)

        if not key:
            msg = "Google API key not found. Set GOOGLE_API_KEY environment variable or add it to your .env file."
            raise MissingApiKeyError(msg)

        from google import genai

        self.client = genai.Client(api_key=key)
        self.model = "gemini-2.0-flash"

    def extract_pages(self, document: PdfDocument) -> list[PdfPage]:
        from google.genai import types

        pages = []
        for page_num, page in enumerate(document):
            logger.debug("Extracting text from page %d via Gemini", page_num + 1)

            pixmap = page.get_pixmap(dpi=300)
            image_bytes = pixmap.tobytes("png")

            response = self.client.models.generate_content(
                model=self.model,
                contents=types.Content(
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                        types.Part.from_text(text=EXTRACTION_PROMPT),
                    ]
                ),
            )

            text = response.text or ""
            if not text.strip():
                logger.warning("Gemini returned empty text for page %d", page_num + 1)

            pages.append(PdfPage(raw_text=text))

        return pages
