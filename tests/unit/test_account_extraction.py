"""Unit tests for account (last-4) extraction: helper + BaseStatement.account."""

import re
from dataclasses import replace

import pytest
from test_utils.statements import StubStatement

from monopoly.config import DateOrder, StatementConfig
from monopoly.constants import EntryType, TransactionKind
from monopoly.pdf import PdfPage
from monopoly.statements import CreditStatement
from monopoly.statements.account_resolver import extract_last4


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
    # BaseStatement is abstract; StubStatement is the minimal instantiable subclass
    return StubStatement(pages=pages, bank_name="example", config=config, header="foo")


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


def _consolidated_config():
    return StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"DATE.*AMOUNT"),
        transaction_pattern=re.compile(
            r"(?P<transaction_date>\d{2} \w{3})\s+(?P<description>.*?)\s+(?P<amount>\d+\.\d{2})$"
        ),
        statement_date_pattern=re.compile(r"(\d{1,2} \w{3} \d{4})"),
        account_pattern=re.compile(r"CARD NO\.:\s*(?P<account>\d{4}(?:\s+\d{4}){3})"),
        statement_date_order=DateOrder("DMY"),
    )


# A consolidated statement: one header per card, each card's rows under it, the second card's
# section running onto the next page.
CONSOLIDATED = [
    PdfPage(
        raw_text="\n".join(
            [
                "STATEMENT DATE 15 Oct 2026",
                "DATE DESCRIPTION AMOUNT",
                "CARD A CARD NO.: 1111 2222 3333 4444",
                "01 Oct SHOP ONE 10.00",
                "02 Oct SHOP TWO 20.00",
                "CARD B CARD NO.: 5555 6666 7777 8888",
                "03 Oct SHOP THREE 30.00",
            ]
        )
    ),
    PdfPage(raw_text="DATE DESCRIPTION AMOUNT\n04 Oct SHOP FOUR 40.00"),
]


def test_each_transaction_takes_the_account_of_its_own_section():
    statement = _statement(CONSOLIDATED, _consolidated_config())

    assert [(t.description, t.account) for t in statement.transactions] == [
        ("SHOP ONE", "4444"),
        ("SHOP TWO", "4444"),
        ("SHOP THREE", "8888"),
        ("SHOP FOUR", "8888"),
    ]
    # the statement-level account stays the first one
    assert statement.account == "4444"


def test_lines_above_the_first_header_take_the_first_account():
    pages = [PdfPage(raw_text="01 Oct EARLY ROW 5.00\nCARD NO.: 1111 2222 3333 4444\n02 Oct LATER ROW 6.00")]
    statement = _statement(pages, _consolidated_config())

    assert [t.account for t in statement.transactions] == ["4444", "4444"]


def test_header_repeated_on_each_page_keeps_one_account():
    header = "CARD NO.: 1111 2222 3333 4444"
    pages = [PdfPage(raw_text=f"{header}\n01 Oct SHOP ONE 10.00"), PdfPage(raw_text=f"{header}\n02 Oct SHOP TWO 20.00")]
    statement = _statement(pages, _consolidated_config())

    assert {t.account for t in statement.transactions} == {"4444"}


def _statement_with_prev_balances(amounts):
    config = replace(
        _consolidated_config(),
        prev_balance_pattern=re.compile(r"(?P<description>PREVIOUS BALANCE)\s+(?P<amount>\d+\.\d{2})"),
    )
    lines = ["STATEMENT DATE 15 Oct 2026"]
    for card, amount, row in zip(("1111 2222 3333 4444", "5555 6666 7777 8888"), amounts, ("01", "02"), strict=True):
        lines += [f"CARD NO.: {card}", f"PREVIOUS BALANCE {amount}", f"{row} Oct SHOP {row} 10.00"]
    pages = [PdfPage(raw_text="\n".join(lines))]
    statement = CreditStatement(pages=pages, bank_name="example", config=config, header="foo")
    return [t for t in statement.transactions if t.kind == TransactionKind.PREVIOUS_BALANCE]


def test_each_previous_balance_takes_the_account_of_its_own_section():
    balances = _statement_with_prev_balances(["100.00", "200.00"])

    assert {abs(t.amount): t.account for t in balances} == {100.0: "4444", 200.0: "8888"}
