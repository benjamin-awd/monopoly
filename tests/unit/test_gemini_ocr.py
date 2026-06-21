import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

from monopoly.ocr import MissingApiKeyError
from monopoly.pdf import PdfPage


@pytest.fixture
def mock_google_genai():
    """Mock the google.genai module since it's an optional dependency."""
    mock_genai = MagicMock()
    mock_google = MagicMock()
    mock_google.genai = mock_genai
    with patch.dict(
        sys.modules, {"google": mock_google, "google.genai": mock_genai, "google.genai.types": mock_genai.types}
    ):
        yield mock_genai


def test_missing_google_genai_package():
    with patch.dict(sys.modules, {"google": None, "google.genai": None}):
        from monopoly.ocr import GeminiOcr

        with pytest.raises(ImportError, match="google-genai is not installed"):
            GeminiOcr(api_key="test-key")


def test_missing_api_key(mock_google_genai, monkeypatch):
    from monopoly.ocr import GeminiOcr

    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(MissingApiKeyError, match="Google API key not found"):
        GeminiOcr()


def test_extract_pages(mock_google_genai):
    from monopoly.ocr import GeminiOcr

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "01 JAN  COFFEE SHOP  5.00\n02 JAN  GROCERY STORE  25.00"
    mock_client.models.generate_content.return_value = mock_response
    mock_google_genai.Client.return_value = mock_client

    mock_page = MagicMock()
    mock_pixmap = MagicMock()
    mock_pixmap.tobytes.return_value = b"fake-png-bytes"
    mock_page.get_pixmap.return_value = mock_pixmap

    mock_document = MagicMock()
    mock_document.__iter__ = Mock(return_value=iter([mock_page]))

    ocr = GeminiOcr(api_key="test-key")
    pages = ocr.extract_pages(mock_document)

    assert len(pages) == 1
    assert isinstance(pages[0], PdfPage)
    assert "COFFEE SHOP" in pages[0].raw_text
    assert "GROCERY STORE" in pages[0].raw_text
    mock_page.get_pixmap.assert_called_once_with(dpi=300)


def test_extract_pages_empty_response(mock_google_genai):
    from monopoly.ocr import GeminiOcr

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = ""
    mock_client.models.generate_content.return_value = mock_response
    mock_google_genai.Client.return_value = mock_client

    mock_page = MagicMock()
    mock_pixmap = MagicMock()
    mock_pixmap.tobytes.return_value = b"fake-png-bytes"
    mock_page.get_pixmap.return_value = mock_pixmap

    mock_document = MagicMock()
    mock_document.__iter__ = Mock(return_value=iter([mock_page]))

    ocr = GeminiOcr(api_key="test-key")
    pages = ocr.extract_pages(mock_document)

    assert len(pages) == 1
    assert pages[0].raw_text == ""
