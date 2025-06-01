import logging
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime

from dateparser import parse

from monopoly.constants.date import ISO8601
from monopoly.enums import RegexEnum
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)

MAX_EXPECTED_DATE_SPANS = 2  # Max expected spans (e.g., transaction date + posting date)
MIN_ADDITIONAL_SPAN_RATIO = 0.5  # Threshold to consider other spans


@dataclass
class DateMatch:
    """
    Helper class that holds information about a match.

    Includes the span (start pos and end pos), the parsed date, the raw date, the line and
    page number, as well as the entire line that was matched.
    """

    span: tuple[int, int]
    parsed_date: datetime
    raw_date: str
    page_number: int
    line_number: int
    line: str


@dataclass
class DatePattern:
    regex: RegexEnum
    num_matches: int = 0
    matches: list[DateMatch] = field(default_factory=list)
    spans: list[tuple] = field(default_factory=list)

    def add_occurrence(self, matches: list[DateMatch]):
        """Add an occurrence and update the span list."""
        for match in matches:
            self.num_matches += 1
            self.matches.append(match)
            self.spans.append(match.span)

    @property
    def name(self) -> str:
        return self.regex.name.lower()

    @property
    def unique_spans(self):
        return set(self.spans)

    @property
    def span_occurrences(self) -> Counter:
        """Counts the number of occurrences per span."""
        return Counter(self.spans)

    @property
    def matched_lines(self) -> list[str] | None:
        """Shows lines that are possible transactions."""
        lines_with_dates = [match.line for match in self.matches if match.span in self.unique_spans]

        return lines_with_dates or None


# pylint: disable=too-many-instance-attributes
class PatternMatcher:
    """Holds date regex patterns used by the generic statement handler."""

    def __iter__(self) -> Iterator[DatePattern]:
        iso8601 = [e.lower() for e in ISO8601._member_names_]
        attr_names = [name for name in dir(self) if name in iso8601]
        for attr_name in attr_names:
            attr = getattr(self, attr_name)
            if isinstance(attr, DatePattern):
                yield attr

    def __init__(self, pages: list[PdfPage]):
        self.pages = pages
        self.set_date_patterns()
        self.get_matches()

    def set_date_patterns(self):
        self.dd_mm = DatePattern(ISO8601.DD_MM)
        self.dd_mm_yy = DatePattern(ISO8601.DD_MM_YY)
        self.dd_mmm = DatePattern(ISO8601.DD_MMM)
        self.dd_mmm_yy = DatePattern(ISO8601.DD_MMM_YY)
        self.dd_mmm_yyyy = DatePattern(ISO8601.DD_MMM_YYYY)
        self.mmmm_dd_yyyy = DatePattern(ISO8601.MMMM_DD_YYYY)
        self.mmm_dd = DatePattern(ISO8601.MMM_DD)
        self.mmm_dd_yyyy = DatePattern(ISO8601.MMM_DD_YYYY)

    def get_matches(self):
        """
        Iterate over all possible date patterns and retrieves transactions lines.

        This is based on the assumption that a transaction line will always start with a date.
        """
        logger.debug("Iterating over patterns: %s", [p.name for p in self])
        for pattern in self:
            logger.debug("Searching for date matches for pattern %s", pattern.name)
            for i, page in enumerate(self.pages):
                for j, line in enumerate(page.lines):
                    if matches := self._extract_match(pattern, line, i, j):
                        pattern.add_occurrence(matches)

    def _extract_match(self, pattern: DatePattern, line: str, page_num: int, line_num: int) -> list[DateMatch]:
        matches = []
        for date_match in pattern.regex.finditer(line):
            raw_date = date_match.group()
            parsed_date = parse(raw_date)
            if parsed_date:
                matches.append(
                    DateMatch(
                        span=(date_match.start(), date_match.end()),
                        parsed_date=parsed_date,
                        raw_date=raw_date,
                        page_number=page_num,
                        line_number=line_num,
                        line=date_match.string,
                    )
                )
                logger.debug(
                    "Date match found at page %s line %s: raw_date='%s' parsed_date='%s'",
                    page_num,
                    line_num,
                    raw_date,
                    parsed_date,
                )
        return matches

    def get_transaction_pattern(self) -> DatePattern:
        """
        Find the pattern that has the highest occurrence of spans over several lines.

        For example, a line like '01 Oct  <description>' has a span of (0, 6) - we then
        check for repeats of this span, and sum it over all lines.

        Patterns ending with "yy" are analyzed first, to avoid cases where we have
        a tiebreaker with dd_mm and dd_mm_yy variants.
        """
        max_span_occurrences = 0
        most_common_pattern = None

        # Sort patterns so that those ending with "yy" come last
        sorted_patterns = sorted(self, key=lambda p: p.name.endswith("yy"))

        for pattern in sorted_patterns:
            if counter := pattern.span_occurrences:
                for _, num_occurrences in counter.most_common(2):
                    if num_occurrences >= max_span_occurrences:
                        most_common_pattern = pattern
                        max_span_occurrences = num_occurrences

        if most_common_pattern:
            logger.debug(
                "Pattern '%s' matched %s times",
                most_common_pattern.name,
                max_span_occurrences,
            )

        if not most_common_pattern:
            msg = "Unable to detect most common pattern"
            raise ValueError(msg)

        return most_common_pattern

    def get_transaction_spans(self, pattern: DatePattern) -> set:
        """
        Return the most probable transactions spans based on occurrences.

        If there are two spans with the same number of occurrences e.g. (0, 6) has 17
        occurrences and (11, 17) has 17 occurrences, we return both
        spans since there is a strong likelihood that one is a transaction date,
        and the other is a posting date.
        """
        max_span_occurrences = 0
        most_common_spans = set()

        counter = pattern.span_occurrences
        for span, num_occurrences in counter.most_common(2):
            if num_occurrences >= max_span_occurrences:
                max_span_occurrences = num_occurrences
                most_common_spans.add(span)

        # Check for additional spans with occurrences >= 50% of the max span occurrences
        if len(most_common_spans) == 1:
            for span, num_occurrences in counter.items():
                if span not in most_common_spans:
                    break

                if num_occurrences > max_span_occurrences * MIN_ADDITIONAL_SPAN_RATIO:
                    most_common_spans.add(span)
                    logger.debug("Adding additional span: %s", span)
                    break

        logger.debug("Most common span(s): %s", most_common_spans)

        if len(most_common_spans) > MAX_EXPECTED_DATE_SPANS:
            msg = "More than two date spans found in statement"
            raise ValueError(msg)

        return most_common_spans

    def get_statement_date_pattern(self) -> str:
        """Create a regex pattern for the statement date based on the first statement date."""
        patterns_with_year = [p for p in self if p.name.endswith("yy")]
        yyyy_matches = {}
        for pattern in patterns_with_year:
            if pattern.matches:
                yyyy_matches[pattern.name] = pattern.matches

        if not yyyy_matches:
            msg = "No lines with `yy` or `yyyy` dates - unable to create statement date pattern"
            raise RuntimeError(msg)

        # try yyyy patterns first before yy
        sorted_patterns: list[str] = sorted(yyyy_matches.keys(), key=lambda p: not p.endswith("yyyy"))
        unsorted_lines: list[tuple[str, DateMatch]] = []

        for pattern_name in sorted_patterns:
            lines = yyyy_matches[pattern_name]
            unsorted_lines.extend((pattern_name, line) for line in lines)

        sorted_lines: list[tuple[str, DateMatch]] = sorted(
            unsorted_lines, key=lambda x: (x[1].page_number, x[1].line_number)
        )

        _, date_match = sorted_lines[0]
        statement_date = date_match.raw_date
        logger.debug("Found statement date: %s", statement_date)

        # assume the statement date is the first parsable YYYY date
        return statement_date
