import logging
import re
from dataclasses import dataclass
from datetime import date

from dateparser import parse

from monopoly.config import StatementConfig
from monopoly.pdf import PdfPage
from monopoly.statements.transaction import strip_non_numeric

logger = logging.getLogger(__name__)


@dataclass
class PaymentSummary:
    """
    The payment summary of a credit statement.

    These are the summary figures printed on a credit card statement that
    describe what (and by when) the cardholder must pay, as opposed to the
    individual transactions. Any field may be ``None`` if the relevant
    pattern is not configured for the bank, or cannot be found in the
    statement.

    - `payment_due_date` is the date by which payment must be made.
    - `total_amount_due` is the full statement balance owed.
    - `minimum_payment` is the smallest amount payable to avoid a late charge.
    """

    payment_due_date: date | None = None
    total_amount_due: float | None = None
    minimum_payment: float | None = None


class PaymentSummaryExtractor:
    """
    Extract a `PaymentSummary` from a credit statement's pages.

    Each field is located by its own optional regex pattern (see
    `PaymentSummaryConfig`), searched line-by-line across every page. Amount
    patterns are expected to expose a named `amount` group, and the date
    pattern a named `due_date` group.
    """

    def __init__(self, pages: list[PdfPage], config: StatementConfig):
        self.pages = pages
        self.patterns = config.payment_summary_config
        self.date_order = config.statement_date_order

    def extract(self) -> PaymentSummary:
        if not self.patterns:
            return PaymentSummary()

        return PaymentSummary(
            payment_due_date=self._extract_date(self.patterns.payment_due_date),
            total_amount_due=self._extract_amount(self.patterns.total_amount_due),
            minimum_payment=self._extract_amount(self.patterns.minimum_payment),
        )

    def _search(self, pattern) -> re.Match | None:
        """Return the first match of `pattern` across all page lines."""
        if not pattern:
            return None
        for page in self.pages:
            for line in page.lines:
                if match := pattern.search(line):
                    return match
        return None

    def _extract_amount(self, pattern) -> float | None:
        if match := self._search(pattern):
            amount = match.group("amount")
            cleaned = strip_non_numeric(amount)
            if cleaned:
                value = float(cleaned)
                return -abs(value) if self._is_credit(match, amount) else value
        return None

    @staticmethod
    def _is_credit(match: re.Match, amount: str) -> bool:
        """
        Return True if the amount represents a credit balance (e.g. an overpayment).

        Credit balances are printed either enclosed in parentheses (``(412.16)``)
        or with a trailing ``CR``/``-`` direction, both of which `strip_non_numeric`
        discards. Without this, a credit balance would be reported as a positive
        amount owed instead of a negative one.
        """
        if amount.strip().startswith("("):
            return True
        if "direction" in match.re.groupindex:
            return match.group("direction") in ("CR", "-")
        return False

    def _extract_date(self, pattern) -> date | None:
        if match := self._search(pattern):
            parsed = parse(match.group("due_date"), settings=self.date_order.settings)
            if parsed:
                return parsed.date()
            logger.debug("Could not parse payment due date: %s", match.group("due_date"))
        return None
