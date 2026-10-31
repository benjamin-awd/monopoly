import pytest

from monopoly.banks.capitalone.capitalone_us import CapitalOneUS
from monopoly.statements.base import TRAILING_AMOUNT, merge_wrapped_amounts

PATTERN = CapitalOneUS.debit.transaction_pattern

ROW = "Mar 15       Withdrawal to 360 Performance Savings...5678       Debit     - $500.00     $1,108.15"
WRAPPED = [
    "Mar 20       Withdrawal from EXAMPLE TAX AUTHORITY ESTIMATED   Debit                   $1,008.15",
    "             PAYMENT                                                     - $100.00",
]


def test_amount_on_the_next_line_is_laid_back_onto_its_row():
    merged = merge_wrapped_amounts(WRAPPED, PATTERN)

    match = PATTERN.search(merged[0])
    assert match
    assert match.group("amount") == "100.00"
    assert match.group("direction") == "-"
    assert match.group("balance") == "1,008.15"
    # the description's wrapped words stay behind for multiline_descriptions
    assert merged[1].strip() == "PAYMENT"


def test_lines_that_already_match_are_left_alone():
    lines = [ROW, "             PAYMENT                                         - $100.00"]

    assert merge_wrapped_amounts(lines, PATTERN) == lines


def test_amount_under_a_filled_column_is_left_alone():
    """The figure below would land on text, so it isn't this row's amount."""
    lines = [
        "Mar 20       Withdrawal from EXAMPLE TAX AUTHORITY ESTIMATED PAYMENTS AND MORE TEXT  $1,008.15",
        "             PAYMENT                                                     - $100.00",
    ]

    assert merge_wrapped_amounts(lines, PATTERN) == lines


def test_a_merge_that_still_does_not_match_is_dropped():
    """An opening balance followed by a figure is not a row: nothing changes."""
    lines = [
        "Mar 1        Opening Balance                                                $2,500.00",
        "                                                                 $12.40",
    ]

    assert merge_wrapped_amounts(lines, PATTERN) == lines


def test_last_line_and_empty_input():
    assert merge_wrapped_amounts([], PATTERN) == []
    assert merge_wrapped_amounts([WRAPPED[0]], PATTERN) == [WRAPPED[0]]


@pytest.mark.parametrize(
    "amount", ["- $1,234.56", "+ £0.12", "- ¥100.00", "- S$100.00", "- HK$100.00", "RM5.00", "100.00"]
)
def test_trailing_amount_takes_the_whole_figure(amount):
    assert TRAILING_AMOUNT.search(f"PAYMENT     {amount}").group() == amount
