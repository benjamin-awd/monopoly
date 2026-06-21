import json
import logging
from datetime import datetime

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from monopoly.pdf import PdfDocument
from monopoly.statements.transaction import Transaction

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """\
Extract all transactions from this bank statement image.

Return a JSON object with exactly this structure:
{
  "statement_date": "YYYY-MM-DD",
  "bank_name": "bank name",
  "statement_type": "credit",
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "description": "merchant or description",
      "amount": -12.34
    }
  ]
}

Rules:
- statement_date: the end date of the statement period
- bank_name: lowercase with underscores (e.g. "hsbc", "bank_of_america")
- statement_type: "credit" for credit card statements, "debit" for bank account/savings/current account statements
- amount: negative for debits/purchases, positive for credits/payments/refunds
- date: the transaction date (not the posting date)
- Include "Previous Statement Balance" or similar balance carry-forward lines as transactions \
(use the statement start date as the date). These are needed for totals to balance.
- Ignore other non-transaction lines (headers, footers, summaries, fine print)
- Return ONLY the JSON object, no markdown fences or commentary
"""


class MissingApiKeyError(Exception):
    """Raised when a required API key is not configured."""


class GeminiSettings(BaseSettings):
    google_api_key: SecretStr | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


class GeminiResult:
    def __init__(
        self, transactions: list[Transaction], statement_date: datetime, bank_name: str, statement_type: str = "credit"
    ):
        self.transactions = transactions
        self.statement_date = statement_date
        self.bank_name = bank_name
        self.statement_type = statement_type


class GeminiParser:
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

        self.client = genai.Client(api_key=key)
        self.model = "gemini-2.5-flash"

    def parse(self, document: PdfDocument) -> GeminiResult:
        from google.genai import types

        parts = []
        for page in document:
            pixmap = page.get_pixmap(dpi=300)
            image_bytes = pixmap.tobytes("png")
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))

        prompt = EXTRACTION_PROMPT
        if document.file_path:
            filename = document.file_path if isinstance(document.file_path, str) else document.file_path.name
            prompt += f"\n\nThe source filename is: {filename}"

        parts.append(types.Part.from_text(text=prompt))

        logger.debug("Sending %d page(s) to Gemini for extraction", len(parts) - 1)

        response = self.client.models.generate_content(
            model=self.model,
            contents=types.Content(parts=parts),
        )

        text = response.text or ""
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
            text = text.strip()

        data = json.loads(text)

        statement_date = datetime.strptime(data["statement_date"], "%Y-%m-%d").astimezone()
        bank_name = data.get("bank_name", "unknown")
        statement_type = data.get("statement_type", "credit")

        transactions = []
        for tx in data["transactions"]:
            transaction = Transaction(
                transaction_date=tx["date"],
                description=tx["description"],
                amount=float(tx["amount"]),
                auto_polarity=False,
            )
            transactions.append(transaction)

        logger.debug("Gemini extracted %d transactions", len(transactions))

        return GeminiResult(
            transactions=transactions,
            statement_date=statement_date,
            bank_name=bank_name,
            statement_type=statement_type,
        )
