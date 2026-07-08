"""Regression tests for the UOB debit statement transaction pattern.

UOB current/savings account statements print a running balance next to every
transaction, but also contain single-number lines (e.g. "BALANCE B/F" and
summary-page amounts) that must not be picked up as transactions.
"""

from monopoly.banks import Uob

pattern = Uob.debit.transaction_pattern


def test_matches_withdrawal_with_running_balance():
    match = pattern.search("04 Jun             Debit Card Payment                29.55                     8,731.74")
    assert match is not None
    assert match.group("transaction_date") == "04 Jun"
    assert match.group("amount") == "29.55"
    assert match.group("balance") == "8,731.74"


def test_matches_deposit_with_running_balance():
    match = pattern.search("22 Jun             Funds Transfer                                 200.00         6,827.49")
    assert match is not None
    assert match.group("amount") == "200.00"
    assert match.group("balance") == "6,827.49"


def test_ignores_balance_brought_forward():
    # "BALANCE B/F" only carries a balance, with no amount + running balance pair
    assert pattern.search("01 Jun             BALANCE B/F                                        8,761.29") is None


def test_ignores_summary_page_amount():
    # a date appearing mid-line on the summary page, with a single trailing number
    assert pattern.search("Locked Amount as of 30 Jun 2026 is 0.00") is None
