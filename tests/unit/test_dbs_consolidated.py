"""DBS/POSB consolidated (deposit account) statements: which lines are transactions, and the account."""

import pytest

from monopoly.banks import Dbs

PATTERN = Dbs.consolidated.transaction_pattern
ACCOUNT = Dbs.consolidated.account_pattern


@pytest.mark.parametrize(
    ("line", "description", "amount"),
    [
        (
            "05/06/2023     CARD PURCHASE EXAMPLE SHOP                 4.90             20.67",
            "CARD PURCHASE EXAMPLE SHOP",
            "4.90",
        ),
        (
            "24/06/2023     FUNDS TRANSFER EXAMPLE                                 2,000.00          20.66",
            "FUNDS TRANSFER EXAMPLE",
            "2,000.00",
        ),
    ],
)
def test_transaction_rows_match(line, description, amount):
    match = PATTERN.search(line)
    assert match
    assert match.group("description") == description
    assert match.group("amount") == amount


def test_balance_only_closing_line_is_not_a_transaction():
    # the account's closing line: a date and its balance, nothing withdrawn or deposited
    assert PATTERN.search("30/06/2023                                                                20.66") is None


def test_account_comes_from_the_summary_row():
    match = ACCOUNT.search("DBS Multiplier Account                           123-4-567890          SGD        1,234.56")
    assert match
    assert match.group("account") == "123-4-567890"
    assert ACCOUNT.search("Balance Brought Forward                                        SGD 25.57") is None
