"""Unit tests for account (last-4) extraction: helper + BaseStatement.account."""

import re

import pytest

from monopoly.config import DateOrder, StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfPage
from monopoly.statements.base import BaseStatement, extract_last4


@pytest.mark.parametrize(
    "token, expected",
    [
        ("4417 88XX XXXX 2031", "2031"),  # masked spaced card number
        ("4111-2222-3333-4444", "4444"),  # dash-separated card number
        ("098-7-654321", "4321"),  # dash-separated account number
        ("987654321098", "1098"),  # bare digits
        ("1234", "1234"),  # exactly four digits
        (None, None),  # nothing matched
        ("XX", None),  # fewer than four digits
        ("12-3", None),  # only three digits present
    ],
)
def test_extract_last4(token, expected):
    assert extract_last4(token) == expected


def _config_with_account_pattern(pattern):
    return StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"DATE.*AMOUNT"),
        transaction_pattern=re.compile(r"\d{2} \w{3}.*\d+\.\d+"),
        statement_date_pattern=re.compile(r"(\d{1,2} \w{3} \d{4})"),
        account_pattern=pattern,
        statement_date_order=DateOrder("DMY"),
    )


def _statement(pages, config):
    return BaseStatement(pages=pages, bank_name="example", config=config, header="foo")


def test_account_none_when_no_pattern_configured():
    config = _config_with_account_pattern(None)
    statement = _statement([PdfPage(raw_text="Account No. 987654321098")], config)

    assert statement.account is None


def test_account_extracts_last4_from_content():
    config = _config_with_account_pattern(re.compile(r"Account No\.\s+(?P<account>\d+)"))
    statement = _statement([PdfPage(raw_text="Account No. 987654321098\nother line")], config)

    assert statement.account == "1098"


def test_account_searches_across_pages():
    config = _config_with_account_pattern(re.compile(r"Account No\.\s+(?P<account>\d+)"))
    pages = [
        PdfPage(raw_text="first page, no account here"),
        PdfPage(raw_text="Account No. 111122223333"),
    ]
    statement = _statement(pages, config)

    assert statement.account == "3333"


def test_account_none_when_pattern_configured_but_no_match():
    config = _config_with_account_pattern(re.compile(r"Account No\.\s+(?P<account>\d+)"))
    statement = _statement([PdfPage(raw_text="no account line present")], config)

    assert statement.account is None
