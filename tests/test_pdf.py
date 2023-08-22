import pytest

from monopoly.pdf import PDF


def test_can_open_protected(pdf: PDF):
    pdf.file_path = "tests/ocbc_365_protected.pdf"
    pdf.password = "foobar123"

    pdf._open_pdf()


def test_wrong_password_raises_error(pdf: PDF):
    pdf.file_path = "tests/ocbc_365_protected.pdf"
    pdf.password = "wrong_pw"

    with pytest.raises(ValueError, match="document is encrypted"):
        pdf._open_pdf()
