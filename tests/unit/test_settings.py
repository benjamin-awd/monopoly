import os
from textwrap import dedent
from unittest import mock

import pytest

from monopoly.config import PdfPasswords, Settings


@pytest.fixture
def mock_env():
    with mock.patch.dict(os.environ, clear=True):
        yield


@pytest.fixture
def create_temporary_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_content = dedent(
        """
    OCBC_PDF_PASSWORDS=["password1", "password2"]
    HSBC_PDF_PASSWORDS=["hsbc_password"]
    """
    )
    env_file.write_text(env_content)
    return str(env_file)


def test_load_from_environment_variable():
    os.environ["PASSWORDS"] = '{"OCBC_PDF_PASSWORDS": ["password1", "password2"]}'
    expected_passwords = ["password1", "password2"]

    settings = Settings().passwords
    assert [
        pw.get_secret_value() for pw in settings.ocbc_pdf_passwords
    ] == expected_passwords


def test_load_from_env_file(create_temporary_env_file, mock_env):
    env_file = create_temporary_env_file
    settings = PdfPasswords(_env_file=env_file)
    expected_ocbc_passwords = ["password1", "password2"]
    expected_hsbc_passwords = ["hsbc_password"]
    assert [
        pw.get_secret_value() for pw in settings.ocbc_pdf_passwords
    ] == expected_ocbc_passwords
    assert [
        pw.get_secret_value() for pw in settings.hsbc_pdf_passwords
    ] == expected_hsbc_passwords
