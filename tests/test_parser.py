import pytest

from monopoly.pdf import PdfParser


def test_can_open_protected(parser: PdfParser):
    parser.file_path = "tests/ocbc_365_protected.pdf"
    parser.password = "foobar123"

    parser.open()


def test_wrong_password_raises_error(parser: PdfParser):
    parser.file_path = "tests/ocbc_365_protected.pdf"
    parser.password = "wrong_pw"

    with pytest.raises(ValueError, match="document is encrypted"):
        parser.open()
