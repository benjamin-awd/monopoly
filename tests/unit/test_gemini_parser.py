import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

from monopoly.gemini import GeminiParser, GeminiResult, MissingApiKeyError


@pytest.fixture
def mock_google_genai():
    mock_genai = MagicMock()
    mock_google = MagicMock()
    mock_google.genai = mock_genai
    with patch.dict(
        sys.modules, {"google": mock_google, "google.genai": mock_genai, "google.genai.types": mock_genai.types}
    ):
        yield mock_genai


def test_missing_google_genai_package():
    with patch.dict(sys.modules, {"google": None, "google.genai": None}):
        with pytest.raises(ImportError, match="google-genai is not installed"):
            GeminiParser(api_key="test-key")


def test_missing_api_key(mock_google_genai, monkeypatch, tmp_path):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(MissingApiKeyError, match="Google API key not found"):
        GeminiParser()


def test_parse_returns_transactions(mock_google_genai):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = """{
        "statement_date": "2026-06-21",
        "bank_name": "hsbc",
        "transactions": [
            {"date": "2026-05-20", "description": "COFFEE SHOP", "amount": -5.00},
            {"date": "2026-05-21", "description": "PAYMENT - THANK YOU", "amount": 100.00}
        ]
    }"""
    mock_client.models.generate_content.return_value = mock_response
    mock_google_genai.Client.return_value = mock_client

    mock_page = MagicMock()
    mock_pixmap = MagicMock()
    mock_pixmap.tobytes.return_value = b"fake-png-bytes"
    mock_page.get_pixmap.return_value = mock_pixmap

    mock_document = MagicMock()
    mock_document.__iter__ = Mock(return_value=iter([mock_page]))

    parser = GeminiParser(api_key="test-key")
    result = parser.parse(mock_document)

    assert isinstance(result, GeminiResult)
    assert len(result.transactions) == 2
    assert result.bank_name == "hsbc"
    assert result.statement_date.year == 2026
    assert result.statement_date.month == 6
    assert result.transactions[0].description == "COFFEE SHOP"
    assert result.transactions[0].amount == -5.00
    assert result.transactions[1].amount == 100.00


def test_parse_strips_markdown_fences(mock_google_genai):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = """```json
{
    "statement_date": "2026-01-15",
    "bank_name": "dbs",
    "transactions": [
        {"date": "2026-01-01", "description": "GROCERY", "amount": -12.34}
    ]
}
```"""
    mock_client.models.generate_content.return_value = mock_response
    mock_google_genai.Client.return_value = mock_client

    mock_page = MagicMock()
    mock_pixmap = MagicMock()
    mock_pixmap.tobytes.return_value = b"fake-png-bytes"
    mock_page.get_pixmap.return_value = mock_pixmap

    mock_document = MagicMock()
    mock_document.__iter__ = Mock(return_value=iter([mock_page]))

    parser = GeminiParser(api_key="test-key")
    result = parser.parse(mock_document)

    assert len(result.transactions) == 1
    assert result.transactions[0].description == "GROCERY"
