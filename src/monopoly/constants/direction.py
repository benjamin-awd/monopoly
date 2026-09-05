"""The accounting direction of a transaction, and the raw markers that encode it."""

from strenum import StrEnum


class Direction(StrEnum):
    """
    Whether a transaction moves money in or out, as stored and serialized.

    The values are the stored form: they appear verbatim in the JSON envelope
    and in the `direction` CSV column, so they must not change without a
    schema bump.
    """

    CREDIT = "credit"
    DEBIT = "debit"

    @classmethod
    def parse(cls, marker: "str | Direction | None", *, minus: "Direction") -> "Direction | None":
        r"""
        Read the raw marker a statement prints beside an amount.

        Statements annotate amounts with a short marker captured by
        `SharedPatterns.DIRECTION` (``CR``, ``DR``, ``DB``, ``+``, ``-``).
        This is the only place that knows that vocabulary.

        `minus` names how a bare ``-`` reads, which genuinely differs by
        statement type: credit statements print it on refunds (a credit),
        debit statements on withdrawals (a debit). Callers pass their
        `minus_direction`.

        Returns `None` when there is no marker at all, leaving the direction
        to be inferred downstream from the sign of the amount.
        """
        match marker:
            case Direction():
                return marker  # already parsed; keep parse() idempotent
            case None | "":
                return None
            case "CR" | "+":
                return cls.CREDIT
            case "DR" | "DB":
                return cls.DEBIT
            case "-":
                return minus
            case _:
                msg = f"Unsupported direction marker {marker!r}"
                raise ValueError(msg)
