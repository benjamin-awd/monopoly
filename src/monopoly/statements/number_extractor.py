"""Number extraction logic for statement safety checks."""

import re

from monopoly.constants import Columns, SharedPatterns
from monopoly.pdf import PdfPage

_NUMBER_RE = re.compile(r"[\d.,]+")
_DECIMAL_RE = re.compile(r"\d+\.\d+$")
_SUBTOTAL_RE = re.compile(rf"(?:sub\stotal.*?)\s+{SharedPatterns.AMOUNT}", re.IGNORECASE)


class NumberExtractor:
    """Extracts decimal numbers from statement pages for safety validation."""

    def __init__(self, pages: list[PdfPage]):
        self.pages = pages

    def get_all_numbers(self) -> set[float]:
        """Extract all decimal numbers from all pages plus subtotal sums."""
        numbers: set[float] = set()
        for page in self.pages:
            numbers.update(self._get_decimal_numbers(page.lines))
        numbers.add(self._get_subtotal_sum())
        return numbers

    def _get_decimal_numbers(self, lines: list[str]) -> set[float]:
        """
        Return all decimal numbers from a list of lines.

        This is used to perform a safety check, to make sure no transactions have been missed.
        """
        numbers: set[str] = set()
        for line in lines:
            numbers.update(_NUMBER_RE.findall(line))
        numbers = {number.replace(",", "") for number in numbers}
        return {float(number) for number in numbers if _DECIMAL_RE.match(number)}

    def _get_subtotal_sum(self) -> float:
        """
        Retrieve the subtotals from a document, and calculates the total.

        Useful for statements that don't give a total figure over
        several cards/months in a single statement.
        """
        subtotals: list[str] = []
        for page in self.pages:
            subtotals.extend(
                match.groupdict()[Columns.AMOUNT] for line in page.lines if (match := _SUBTOTAL_RE.search(line))
            )
        cleaned_subtotals = [float(amount.replace(",", "")) for amount in subtotals]
        return sum(cleaned_subtotals)
