import pytest

from monopoly.constants import Direction


def test_stored_values_are_the_wire_format():
    """`Direction` is a StrEnum, so members compare equal to their stored strings."""
    assert Direction.CREDIT == "credit"
    assert Direction.DEBIT == "debit"


@pytest.mark.parametrize("marker", ["CR", "+"])
def test_credit_markers(marker):
    assert Direction.parse(marker, minus=Direction.DEBIT) is Direction.CREDIT


@pytest.mark.parametrize("marker", ["DR", "DB"])
def test_debit_markers(marker):
    """`DB` is captured by SharedPatterns.DIRECTION and must not raise."""
    assert Direction.parse(marker, minus=Direction.CREDIT) is Direction.DEBIT


@pytest.mark.parametrize("marker", [None, ""])
def test_absent_marker_defers_to_the_caller(marker):
    assert Direction.parse(marker, minus=Direction.DEBIT) is None


@pytest.mark.parametrize(
    ("minus", "expected"),
    [(Direction.DEBIT, Direction.DEBIT), (Direction.CREDIT, Direction.CREDIT)],
)
def test_minus_follows_the_statement_type(minus, expected):
    """A bare '-' is a withdrawal on a debit statement, a refund on a credit one."""
    assert Direction.parse("-", minus=minus) is expected


@pytest.mark.parametrize("value", [Direction.CREDIT, Direction.DEBIT])
def test_parse_is_idempotent(value):
    """Re-parsing an already-parsed value returns it unchanged."""
    assert Direction.parse(value, minus=Direction.DEBIT) is value


def test_unknown_marker_raises():
    with pytest.raises(ValueError, match="Unsupported direction marker 'XX'"):
        Direction.parse("XX", minus=Direction.DEBIT)
