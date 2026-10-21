"""DBS/POSB consolidated statements issued before mid-2021 (StreamServe): header, rows and the account."""

import pytest

from monopoly.banks import Dbs

CONFIG = Dbs.consolidated_legacy
PATTERN = CONFIG.transaction_pattern


def test_legacy_header_is_only_the_legacy_layout():
    assert CONFIG.header_pattern.search("Date          Description            Withdrawal       Deposit       Balance")
    # the later layout marks its columns, and the credit layout has no withdrawal column
    assert not CONFIG.header_pattern.search("Date   Description   Withdrawal (-)   Deposit (+)   Balance")
    assert not CONFIG.header_pattern.search("DATE   DESCRIPTION   AMOUNT (S$)")


def test_legacy_config_is_tried_before_the_credit_config():
    # the statement's debit card summary has a "DATE DESCRIPTION ... AMOUNT" header, which the credit config matches
    assert Dbs.statement_configs.index(CONFIG) < Dbs.statement_configs.index(Dbs.credit)


@pytest.mark.parametrize(
    ("line", "description", "amount"),
    [
        (
            "03 Jun           FAST PAYMENT EXAMPLE SHOP                               25.40         1,234.56",
            "FAST PAYMENT EXAMPLE SHOP",
            "25.40",
        ),
        ("23 Jun           ATM Withdrawal                          50.00", "ATM Withdrawal", "50.00"),
    ],
)
def test_account_rows_match(line, description, amount):
    match = PATTERN.search(line)
    assert match
    assert match.group("description") == description
    assert match.group("amount") == amount


def test_debit_card_summary_rows_are_not_account_rows():
    # the summary after the accounts dates its rows in capitals and repeats card spending already listed above
    assert PATTERN.search("31 MAY    CARD PURCHASE EXAMPLE SHOP        4111 1111 1111 1111          12.34") is None


def test_balance_lines_are_not_transactions():
    assert PATTERN.search("                 Balance Brought Forward                                  1,000.00") is None


def test_account_comes_from_each_account_header():
    match = CONFIG.account_pattern.search("DBS Multiplier Account                      Account No. 123-456789-0")
    assert match
    assert match.group("account") == "123-456789-0"
    assert CONFIG.account_per_section


def test_statement_date():
    assert CONFIG.statement_date_pattern.search("ACCOUNT SUMMARY            |      As at 30 Jun 2019")
