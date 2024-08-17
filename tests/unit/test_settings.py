import os

import pytest

from monopoly.pdf import PdfPasswords


@pytest.fixture
def create_temporary_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_content = 'PDF_PASSWORDS=["passwordfoo", "passwordbar"]'
    env_file.write_text(env_content)
    return str(env_file)


def test_load_from_environment_variable():
    os.environ["PDF_PASSWORDS"] = '["password1", "password2"]'
    expected_passwords = ["password1", "password2"]
    passwords = PdfPasswords().pdf_passwords

    assert [pw.get_secret_value() for pw in passwords] == expected_passwords


@pytest.mark.usefixtures("mock_env")
def test_load_from_env_file(create_temporary_env_file):
    env_file = create_temporary_env_file
    passwords = PdfPasswords(_env_file=env_file).pdf_passwords
    expected_passwords = ["passwordfoo", "passwordbar"]
    assert [pw.get_secret_value() for pw in passwords] == expected_passwords
