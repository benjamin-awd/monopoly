"""Test for entrypoint used by Cloud Run"""
from unittest.mock import Mock, PropertyMock, patch

import pytest

from monopoly.helpers.constants import EmailSubjectRegex
from monopoly.main import process_bank_statement


def run_bank_statement_test(message, pattern, subject, expected_result):
    with patch(
        "monopoly.main.Message.subject", new_callable=PropertyMock
    ) as mock_subject:
        mock_subject.return_value = subject
        bank_class = Mock()
        banks = {pattern: bank_class}

        process_bank_statement(message, banks)

        if expected_result == "call":
            bank_class.assert_called_once()

        else:
            bank_class.assert_not_called()


@pytest.mark.parametrize(
    "subject,pattern,expected_result",
    [
        ("OCBC Bank: Your Credit Card e-Statement", EmailSubjectRegex.OCBC, "call"),
        ("Your HSBC VISA REVOLUTION eStatement", EmailSubjectRegex.HSBC, "call"),
        ("Random Subject", EmailSubjectRegex.OCBC, "ignore"),
    ],
)
def test_process_bank_statements(
    monkeypatch,
    message,
    pattern,
    attachment,
    subject,
    expected_result,
):
    monkeypatch.setattr(message, "get_attachment", lambda: attachment)

    run_bank_statement_test(message, pattern, subject, expected_result)
