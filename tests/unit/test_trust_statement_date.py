import pytest

from monopoly.banks.trust import Trust


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Statement cycle   1 Mar 2025 - 15 Mar 2025", ("15", "Mar", "2025")),
        # A cycle ending on a single-digit day used to raise MissingStatementDateError.
        ("Statement cycle   10 Sep 2026 - 9 Oct 2026", ("9", "Oct", "2026")),
    ],
)
def test_statement_date_accepts_one_or_two_digit_day(line, expected):
    match = Trust.credit.statement_date_pattern.search(line)

    assert match is not None
    assert (match["day"], match["month"], match["year"]) == expected
