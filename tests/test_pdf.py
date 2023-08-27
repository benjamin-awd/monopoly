import pytest

from monopoly.pdf import PDF


def test_can_open_protected(pdf: PDF):
    file_path = "tests/ocbc_365_protected.pdf"
    password = "foobar123"

    pdf.open(file_path, password)


def test_wrong_password_raises_error(pdf: PDF):
    file_path = "tests/ocbc_365_protected.pdf"
    password = "wrong_pw"

    with pytest.raises(ValueError, match="document is encrypted"):
        pdf.open(file_path, password)
