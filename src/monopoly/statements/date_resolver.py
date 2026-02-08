"""Date resolution logic for statement dates."""

import logging
import re
from datetime import datetime
from pathlib import Path

from dateparser import parse

from monopoly.config import StatementConfig
from monopoly.constants.date import ISO8601
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)


class DateResolver:
    """Resolves statement date from PDF content or filename."""

    def __init__(
        self,
        pages: list[PdfPage],
        config: StatementConfig,
        file_path: Path | None = None,
    ):
        self.pages = pages
        self.config = config
        self.multiline_config = config.multiline_config
        self.file_path = file_path

    def resolve(self) -> datetime:
        """Find statement date from content, falling back to filename."""
        pattern = self.config.statement_date_pattern
        allowed_patterns = (re.Pattern, ISO8601)

        if not isinstance(pattern, allowed_patterns):
            msg = f"Pattern must be one of {allowed_patterns}, not {type(pattern)}"
            raise TypeError(msg)

        for page in self.pages:
            lines = page.lines

            for i, line in enumerate(lines):
                text = self._get_search_text(lines, i, line)

                if match := pattern.search(text):
                    date_string = self._construct_date_string(match)
                    statement_date = parse(
                        date_string=date_string,
                        settings=self.config.statement_date_order.settings,
                    )
                    if statement_date:
                        return statement_date
                    logger.info("Unable to parse statement date %s", date_string)

        # Fallback: Try extracting date from filename
        if filename_date := self._extract_date_from_filename():
            logger.info("Statement date extracted from filename: %s", filename_date)
            return filename_date

        msg = "Statement date not found"
        raise ValueError(msg)

    def _get_search_text(self, lines: list[str], i: int, line: str) -> str:
        """Get text to search, optionally combining multiple lines and removing whitespace."""
        if not self.multiline_config:
            return line

        if self.multiline_config.multiline_statement_date:
            return " ".join(" ".join(lines[i : i + 3]).split())

        return line

    @staticmethod
    def _construct_date_string(match: re.Match) -> str:
        """Construct date with named groups 'day', 'month', and 'year' if they exist, otherwise use group 1."""
        if {"day", "month", "year"}.issubset(match.groupdict()):
            day = match.group("day")
            month = match.group("month")
            year = match.group("year")

            return f"{day}-{month}-{year}"
        return match.group(1)

    def _extract_date_from_filename(self) -> datetime | None:
        """
        Extract statement month and year from the filename.

        Only enabled if the bank config has a filename_fallback_pattern set.

        Supports patterns like:
        - eStatement_Nov2025_2025-11-07T14_50_26.pdf
        - CardStatement_Oct2025.pdf

        Returns datetime object with day set to 1, or None if pattern not found.
        """
        if not self.file_path or not self.config.filename_fallback_pattern:
            return None

        filename = self.file_path.name

        if match := self.config.filename_fallback_pattern.search(filename):
            month_abbr = match.group(1)
            year = match.group(2)
            date_string = f"1 {month_abbr} {year}"

            try:
                return parse(
                    date_string=date_string,
                    settings=self.config.statement_date_order.settings,
                )
            except (ValueError, TypeError) as e:
                logger.warning("Failed to parse date from filename '%s': %s", filename, e)
                return None

        return None
