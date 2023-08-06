import pytest
from pikepdf import PasswordError

from monopoly.pdf import PDF


def test_can_open_protected():
    pdf = PDF(file_path="tests/ocbc_365_protected.pdf", password="foobar123")
    pdf._open_pdf()


def test_wrong_password_raises_error():
    pdf = PDF(file_path="tests/ocbc_365_protected.pdf", password="wrongpw")
    with pytest.raises(PasswordError, match="invalid password"):
        pdf._open_pdf()
