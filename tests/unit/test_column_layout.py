import re

import pytest

from monopoly.config import DateOrder, StatementConfig
from monopoly.constants import Direction, EntryType
from monopoly.pdf import PdfPage
from monopoly.statements import DebitStatement
from monopoly.statements.column_layout import ColumnLayout

LAYOUT = ColumnLayout(withdrawal=40, deposit=55)


@pytest.mark.parametrize("end_pos", [38, 40, 42, 47])
def test_amount_nearer_the_withdrawal_column_is_a_debit(end_pos):
    assert LAYOUT.classify(end_pos) is Direction.DEBIT


@pytest.mark.parametrize("end_pos", [48, 53, 55, 60])
def test_amount_nearer_the_deposit_column_is_a_credit(end_pos):
    assert LAYOUT.classify(end_pos) is Direction.CREDIT


def test_equidistant_amount_resolves_to_debit():
    """
    The tie-break must stay on debit.

    `get_debit_direction` returned CREDIT only when the withdrawal distance was
    strictly greater, so an exactly-equidistant amount has always been read as
    a withdrawal. Pinned here so the boundary cannot drift silently.
    """
    midpoint = (LAYOUT.withdrawal + LAYOUT.deposit) // 2
    assert LAYOUT.classify(midpoint) is Direction.DEBIT


def test_layout_at_column_zero_is_usable():
    """A column starting at position 0 is a real layout, not a missing one."""
    layout = ColumnLayout(withdrawal=0, deposit=20)
    assert layout.classify(0) is Direction.DEBIT
    assert layout.classify(20) is Direction.CREDIT


def test_layout_is_frozen():
    with pytest.raises(Exception, match="frozen|immutable|cannot assign"):
        LAYOUT.withdrawal = 99


def test_missing_header_on_page_yields_no_layout():
    """
    A column the page does not contain must not become position -1.

    `get_header_pos` returned `-1` when the header line was absent from a given
    page, and `-1` is truthy — so `get_withdrawal_pos`'s walrus returned it and
    the old `withdrawal_pos and deposit_pos` gate accepted it. Every
    transaction on such a page was then classified against (-1, -1), whose
    distances are equal, forcing DEBIT regardless of the real column.
    """
    config = StatementConfig(
        statement_type=EntryType.DEBIT,
        header_pattern=re.compile(r"(WITHDRAWAL.*DEPOSIT.*BALANCE)"),
        transaction_pattern=re.compile("foo"),
        statement_date_pattern=re.compile(""),
        transaction_date_order=DateOrder("DMY"),
    )
    # `header` was found on some other page; this page does not repeat it
    page = PdfPage("15 OCT   bill payment             322.07\n")
    statement = DebitStatement([page], "bank", config, "date description withdrawal deposit balance")

    assert statement.get_header_pos("withdrawal", 0) is None
    assert statement.get_withdrawal_pos(0) is None
    assert statement.get_deposit_pos(0) is None
    assert statement.column_layouts[0] is None
