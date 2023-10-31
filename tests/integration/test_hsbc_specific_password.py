from pathlib import Path

from monopoly.banks import Hsbc
from monopoly.config import PdfConfig, settings

fixture_directory = Path(__file__).parent / "fixtures"


def test_hsbc_specific_password_instead_of_prefix(monkeypatch, hsbc: Hsbc):
    monkeypatch.setattr("monopoly.config.settings.hsbc_pdf_password", "foobar123")

    class HsbcOverride(Hsbc):
        pdf_config = PdfConfig(
            password=settings.hsbc_pdf_password,
        )

    file_path = fixture_directory / "protected.pdf"
    hsbc_override = HsbcOverride(file_path)

    document = hsbc_override.open()
    assert not document.is_encrypted
