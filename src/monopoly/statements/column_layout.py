"""The withdrawal/deposit column geometry of a debit statement page."""

from dataclasses import dataclass

from monopoly.constants import Direction


@dataclass(frozen=True)
class ColumnLayout:
    """
    Character positions of the withdrawal and deposit columns on one page.

    The two positions are only ever useful together — classifying an amount
    needs both — so they are held as one value. A layout cannot be constructed
    with only one column found, which removes the "withdrawal but no deposit"
    state the caller would otherwise have to consider.
    """

    withdrawal: int
    deposit: int

    def classify(self, amount_end_pos: int) -> Direction:
        """
        Decide which column an amount sits under.

        Amounts are right-aligned beneath their column heading, so the amount's
        final character is compared against each heading's end position and the
        nearer column wins.

        e.g. with WITHDRAWAL ending at 40 and DEPOSIT at 55:
        ```
        DATE     DESCRIPTION          WITHDRAWAL         DEPOSIT
        15 OCT   bill payment             322.07
        16 OCT   item                                     123.12
        ```
        """
        to_withdrawal = abs(amount_end_pos - self.withdrawal)
        to_deposit = abs(amount_end_pos - self.deposit)
        return Direction.CREDIT if to_withdrawal > to_deposit else Direction.DEBIT
