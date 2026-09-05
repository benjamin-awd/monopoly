import json
import logging
import re
from datetime import datetime

from monopoly.constants import TransactionKind
from monopoly.llm import GeminiSettings, MissingApiKeyError
from monopoly.pdf import PdfDocument
from monopoly.statements.transaction import Transaction

logger = logging.getLogger(__name__)

# Safety net for when the model omits the "kind" marker: the wordings the native
# parsers' per-bank ``prev_balance_pattern`` use for carried-over prior balances.
_PREV_BALANCE_RE = re.compile(
    r"""(?ix)
      last\s+month'?s\s+balance
    | previous\s+(statement\s+)?balance
    | balance\s+(previous\s+statement|from\s+previous\s+statement|brought\s+forward)
    | outstanding\s+balance\s+brought\s+forward
    """
)

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
      "amount": -12.34,
      "kind": "transaction"
    }
  ]
}

Rules:
- statement_date: the end date of the statement period
- bank_name: lowercase with underscores (e.g. "hsbc", "bank_of_america")
- statement_type: "credit" for credit card statements, "debit" for bank account/savings/current account statements
- amount: negative for debits/purchases, positive for credits/payments/refunds
- date: the transaction date (not the posting date)
- kind: "transaction" for normal activity, or "previous_balance" for a carried-over prior \
statement balance line (e.g. "Previous Statement Balance", "Last Month's Balance", \
"Balance Brought Forward"). Default to "transaction" when unsure.
- Include the carried-over prior balance line as a row with "kind": "previous_balance" \
(use the statement start date as the date). These are needed for totals to balance.
- Ignore other non-transaction lines (headers, footers, summaries, fine print)
- Return ONLY the JSON object, no markdown fences or commentary
"""


def _resolve_kind(description: str, raw_kind: str | None) -> TransactionKind:
    """
    Map the model's ``kind`` marker to a :class:`TransactionKind`.

    Trusts an explicit marker, but falls back to matching the description against
    the known carry-forward wordings so a model miss doesn't silently regress a
    previous-balance row into ordinary activity.
    """
    if raw_kind:
        try:
            return TransactionKind(raw_kind)
        except ValueError:
            logger.warning("Unknown transaction kind %r from Gemini; treating as transaction", raw_kind)
    if _PREV_BALANCE_RE.search(description or ""):
        return TransactionKind.PREVIOUS_BALANCE
    return TransactionKind.TRANSACTION


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
                auto_direction=False,
                kind=_resolve_kind(tx["description"], tx.get("kind")),
            )
            transactions.append(transaction)

        logger.debug("Gemini extracted %d transactions", len(transactions))

        return GeminiResult(
            transactions=transactions,
            statement_date=statement_date,
            bank_name=bank_name,
            statement_type=statement_type,
        )
