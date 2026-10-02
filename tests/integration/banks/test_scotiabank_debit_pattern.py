"""Regression tests for the Scotiabank personal debit statement patterns.

Personal debit statements print days both zero-padded ("Jan 07") and unpadded
("Jan 7"), in transaction dates and in the closing balance date (see #333).
"""

import pytest

from monopoly.banks import Scotiabank

config = Scotiabank.debit_personal


@pytest.mark.parametrize("date", ["Jan 7", "Jan 07", "Jan 17", "Jan 31"])
def test_matches_transaction_date(date):
    match = config.transaction_pattern.search(f"{date:<10}POS PURCHASE STORE             12.34         1,000.00")
    assert match is not None
    assert match.group("transaction_date") == date
    assert match.group("amount") == "12.34"
    assert match.group("balance") == "1,000.00"


def test_ignores_opening_balance():
    assert config.transaction_pattern.search("Jan 1     Opening Balance       12.34         1,000.00") is None


@pytest.mark.parametrize("date", ["January 9, 2026", "January 09, 2026", "January 31, 2026"])
def test_matches_statement_date(date):
    match = config.statement_date_pattern.search(f"Closing Balance on {date}      $1,000.00")
    assert match is not None
    assert match.group("date") == date
