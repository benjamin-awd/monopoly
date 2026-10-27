"""Unit tests for per-section currencies: the name-to-code helper, CurrencyResolver and DBS consolidated."""

import re

import pytest
from test_utils.statements import StubStatement

from monopoly.banks import Dbs
from monopoly.config import DateOrder, StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfPage
from monopoly.statements import DebitStatement
from monopoly.statements.currency_resolver import to_currency_code


@pytest.mark.parametrize(
    "token, expected",
    [
        ("SINGAPORE DOLLAR", "SGD"),
        ("UNITED STATES DOLLAR", "USD"),
        ("United  States Dollar", "USD"),  # case and spacing don't matter
        ("EUR", "EUR"),  # a code is taken as-is
        ("MARTIAN CREDIT", None),  # an unknown name opens no section
        (None, None),
    ],
)
def test_to_currency_code(token, expected):
    assert to_currency_code(token) == expected


def _config(currency_pattern, currency="SGD"):
    return StatementConfig(
        statement_type=EntryType.DEBIT,
        header_pattern=re.compile(r"DATE.*AMOUNT"),
        transaction_pattern=re.compile(
            r"(?P<transaction_date>\d{2} \w{3})\s+(?P<description>.*?)\s+(?P<amount>\d+\.\d{2})$"
        ),
        statement_date_pattern=re.compile(r"(\d{1,2} \w{3} \d{4})"),
        currency_pattern=currency_pattern,
        statement_date_order=DateOrder("DMY"),
        currency=currency,
    )


def _statement(pages, config):
    return StubStatement(pages=pages, bank_name="example", config=config, header="foo")


SECTIONS = [
    PdfPage(
        raw_text="\n".join(
            [
                "STATEMENT DATE 30 Sep 2026",
                "DATE DESCRIPTION AMOUNT",
                "01 Sep BEFORE ANY SECTION 1.00",
                "CURRENCY: SINGAPORE DOLLAR",
                "02 Sep SHOP ONE 10.00",
                "CURRENCY: UNITED STATES DOLLAR",
                "03 Sep INTEREST 0.30",
            ]
        )
    ),
    PdfPage(raw_text="DATE DESCRIPTION AMOUNT\n04 Sep CARRIED ONTO THE NEXT PAGE 2.00"),
]
CURRENCY = re.compile(r"CURRENCY:\s+(?P<currency>[A-Z][A-Z ]*[A-Z])")


def test_each_transaction_takes_the_currency_of_its_own_section():
    statement = _statement(SECTIONS, _config(CURRENCY))

    assert [(t.description, t.currency) for t in statement.transactions] == [
        ("BEFORE ANY SECTION", "SGD"),  # above every header: the config's currency
        ("SHOP ONE", "SGD"),
        ("INTEREST", "USD"),
        ("CARRIED ONTO THE NEXT PAGE", "USD"),
    ]


def test_without_a_pattern_every_transaction_takes_the_config_currency():
    statement = _statement(SECTIONS, _config(None))

    assert {t.currency for t in statement.transactions} == {"SGD"}


def test_currency_is_part_of_a_transactions_identity():
    one = _statement(SECTIONS, _config(CURRENCY)).transactions
    flat = _statement(SECTIONS, _config(None)).transactions

    # SGD rows keep their fingerprint; a row now known to be in USD gets a different one.
    assert one[1].content_hash == flat[1].content_hash
    assert one[2].content_hash != flat[2].content_hash


# DBS/POSB consolidated statement, multi-currency account: made-up figures in pdftotext's layout.
DBS_MULTI = PdfPage(
    raw_text="\n".join(
        [
            "Transaction Details as at 30 Sep 2026",
            "DBS eMulti-Currency Autosave Account                                   ",
            "Account No. 123-456789-0",
            "Date           Description                                           Withdrawal (-)     Deposit (+)        Balance",
            " CURRENCY: SINGAPORE DOLLAR",
            "               Balance Brought Forward                                                                   SGD 100.00",
            "07/09/2026     GIRO EXAMPLE PAYEE                                    8.00                                92.00",
            "30/09/2026     Monthly Account Fee                                   2.00                                90.00",
            "               Total Balance Carried Forward in SGD:                 10.00              0.00             90.00",
            "Date           Description                                           Withdrawal (-)     Deposit (+)        Balance",
            "CURRENCY: UNITED STATES DOLLAR",
            "               Balance Brought Forward                                                                   USD 1,000.00",
            "30/09/2026     Interest                                                                 0.50          1,000.50",
            "               Total Balance Carried Forward in USD:                 0.00               0.50          1,000.50",
        ]
    )
)


def test_dbs_consolidated_rows_take_their_sections_currency():
    statement = DebitStatement(pages=[DBS_MULTI], bank_name="dbs", config=Dbs.consolidated, header="date")

    assert [(t.description, t.currency) for t in statement.transactions] == [
        ("GIRO EXAMPLE PAYEE", "SGD"),
        ("Monthly Account Fee", "SGD"),
        ("Interest", "USD"),
    ]


@pytest.mark.parametrize(
    "line",
    [
        "Summary of Currency Breakdown:",
        "CURRENCY: SINGAPORE DOLLAR AND MORE 1.00",  # a header has nothing after the name
    ],
)
def test_dbs_currency_header_is_only_the_header_line(line):
    assert Dbs.consolidated.currency_pattern.search(line) is None
