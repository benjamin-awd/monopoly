"""Transaction date normalisation, including cross-year resolution."""

import logging
from datetime import datetime

from monopoly.config import StatementConfig
from monopoly.constants.date import DateFormats

logger = logging.getLogger(__name__)

START_OF_YEAR_MONTHS = (1, 2)
YEAR_CUTOFF_MONTH = 2


class DateTransformer:
    """
    Converts a statement's transaction dates to ISO 8601.

    Most banks print transaction dates without a year, so the year is taken
    from the statement date. That is wrong for a statement issued in January
    or February which still lists December transactions, so those are pushed
    back a year — see `_is_cross_year`.
    """

    def __init__(self, config: StatementConfig, statement_date: datetime):
        self.statement_date = statement_date
        self.date_format = config.transaction_date_format
        self.date_order = config.transaction_date_order

    def to_iso8601(self, date_str: str) -> str:
        """Convert a single date string, resolving its year if it has none."""
        parsed_date, injected_year = self._parse(date_str)

        if injected_year and self._is_cross_year(parsed_date):
            parsed_date = parsed_date.replace(year=parsed_date.year - 1)

        return parsed_date.date().isoformat()

    def _parse(self, date_str: str) -> tuple[datetime, bool]:
        """
        Parse a date string, returning it alongside whether a year was injected.

        `strptime` is tried first because it is markedly faster; `dateparser`
        is the fallback for the formats it cannot handle.
        """
        needs_year = not DateFormats.YYYY.search(date_str) and "y" not in self.date_format.lower()
        fmt = self.date_format

        if needs_year:
            date_str = f"{date_str} {self.statement_date.year}"
            fmt += " %Y"

        try:
            return datetime.strptime(date_str, fmt).astimezone(), needs_year
        except ValueError:
            logger.debug("strptime failed for %s with format %s", date_str, fmt)

        # imported lazily: dateparser is slow to import and rarely needed
        from dateparser import parse

        if parsed_date := parse(date_str, settings=self.date_order.settings):
            return parsed_date, needs_year

        msg = f"Could not convert date: {date_str}"
        raise RuntimeError(msg)

    def _is_cross_year(self, parsed_date: datetime) -> bool:
        """Report whether a Jan/Feb statement is listing a late-year transaction."""
        return self.statement_date.month in START_OF_YEAR_MONTHS and parsed_date.month > YEAR_CUTOFF_MONTH
