import pytest

from monopoly.constants import Direction
from monopoly.statements.base import BaseStatement, MatchContext


def _context(statement: BaseStatement, lines: list[str]) -> MatchContext:
    statement.pages[0].lines = lines
    return MatchContext(
        lines=lines,
        line=lines[0],
        description="PAYMENT RECEIVED - THANK YOU",
        idx=0,
    )


def test_multiline_direction_detected(statement: BaseStatement):
    context = _context(
        statement,
        [
            "24.02.25  PAYMENT RECEIVED - THANK YOU            79.99",
            "                                                  CR",
        ],
    )

    assert statement.get_multiline_direction(context) is Direction.CREDIT


@pytest.mark.parametrize(
    "next_line",
    [
        "  CONTINUATION OF DESCRIPTION",
        "                                                  -50.00",
        "CR  AND THEN SOME MORE TEXT",
        "",
    ],
)
def test_next_line_that_is_not_a_bare_marker_is_ignored(statement: BaseStatement, next_line: str):
    """
    Only a line consisting solely of a marker sets the direction.

    Anything else is statement body; leaving it unset lets the amount's sign
    decide, which is what happened before the marker vocabulary was centralised.
    """
    context = _context(
        statement,
        ["24.02.25  PAYMENT RECEIVED - THANK YOU            79.99", next_line],
    )

    assert statement.get_multiline_direction(context) is None
