import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property, lru_cache

from dateparser import parse

from monopoly.constants import DateRegexPatterns, EntryType, SharedPatterns
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)


@dataclass
class DateMatch:
    """Helper class that holds information about a match, including the span
    (start pos and end pos), the parsed date, the raw date, the line and
    page number, as well as the entire line that was matched
    """

    span: tuple[int, int]
    parsed_date: datetime
    raw_date: str
    page_number: int
    line_number: int
    line: str


class DatePatternAnalyzer:
    def __init__(self, pages: list[PdfPage]):
        self.pages = pages
        self.date_regex_patterns: dict[str, re.Pattern] = (
            DateRegexPatterns().as_pattern_dict()
        )
        self.patterns_with_date_matches = self.get_patterns_with_date_matches()
        self.pattern_spans_mapping = self.find_tuples_with_highest_occurrence(
            self.unique_matches_by_pattern
        )
        self.filtered_lines_with_dates = self.get_filtered_lines_with_dates(
            self.pattern_spans_mapping
        )

    @cached_property
    def unique_matches_by_pattern(self) -> dict:
        return self.count_unique_date_matches()

    @cached_property
    def lines_before_first_transaction(self) -> list[str]:
        first_transaction_line: DateMatch = self.filtered_lines_with_dates[0]
        first_page = self.pages[first_transaction_line.page_number].lines
        return list(reversed(first_page[: first_transaction_line.line_number]))

    def get_patterns_with_date_matches(self) -> dict[str, list[DateMatch]]:
        """Retrieves all possible transactions from every page, based on the assumption
        that a transaction line will always start with a date"""
        results: dict[str, list] = {}
        results = {
            pattern_name: self._find_matches(pattern, pattern_name, self.pages)
            for pattern_name, pattern in self.date_regex_patterns.items()
        }

        # filter out patterns with no matches
        return {k: v for k, v in results.items() if v}

    def _find_matches(
        self, pattern: re.Pattern, pattern_name: str, pages: list[PdfPage]
    ) -> list[DateMatch]:
        matches = []
        logger.debug("Searching for date matches for pattern %s", pattern_name)
        for page_num, page in enumerate(pages):
            for line_num, line in enumerate(page.lines):
                matches.extend(
                    self._extract_date_matches(pattern, line, page_num, line_num)
                )
        return matches

    def _extract_date_matches(
        self, pattern: re.Pattern, line: str, page_num: int, line_num: int
    ) -> list[DateMatch]:
        matches = []
        for date_match in pattern.finditer(line):
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

    def count_unique_date_matches(self) -> dict:
        match_dict: dict = {}

        for pattern_name, matches in self.patterns_with_date_matches.items():
            match_dict[pattern_name] = {}

            unique_matches = set()
            for match in matches:
                unique_matches.add(match.span)

            sorted_unique_matches = sorted(unique_matches)

            for match in sorted_unique_matches:  # type: ignore
                match_dict[pattern_name][match] = 0

            # count number of times each tuple occurs
            for match in matches:
                match_tuple = match.span
                if match_tuple in match_dict[pattern_name]:
                    match_dict[pattern_name][match_tuple] += 1

        logger.debug("Unique matches: %s", match_dict)
        return match_dict

    @staticmethod
    def find_tuples_with_highest_occurrence(
        unique_date_matches: dict[str, dict[tuple, int]]
    ) -> dict:
        """
        Finds one or more tuples with the highest occurrence over several lines.
        For example, a line like '01 Oct  <description>' has a span of (0, 6) - we then
        check for repeats of this span, and sum it over all lines.

        If there are two tuples with the same number of occurrences e.g. (0, 6) has 17
        occurrences and (11, 17) has 17 occurrences, we return both
        tuples since there is a strong likelihood that one is a transaction date,
        and the other is a posting date.

        Patterns ending with "yy" are analyzed first, to avoid cases where we have
        a tiebreaker with dd_mm and dd_mm_yy variants.
        """
        span_occurrences = 0
        most_common_pattern = ""
        most_common_tuples = []

        # Sort patterns so that those ending with "yy" come first
        sorted_patterns = sorted(
            unique_date_matches.keys(), key=lambda p: not p.endswith("yy")
        )

        for pattern in sorted_patterns:
            spans_dict = unique_date_matches[pattern]
            max_span_occurrences = max(unique_date_matches[pattern].values())

            if max_span_occurrences > span_occurrences:
                tuples = [k for k, v in spans_dict.items() if v == max_span_occurrences]
                span_occurrences = max_span_occurrences
                most_common_pattern = pattern
                most_common_tuples = tuples

        logger.debug(
            "Pattern %s matched %s times at span(s) %s",
            most_common_pattern,
            span_occurrences,
            most_common_tuples,
        )

        # If the another span tuple pair occurs
        # at a rate of at least 0.5x the most common pair,
        # add it to the most_common_tuples list
        # this adds tolerance for tuples that may be misaligned across pages
        # e.g. {(3, 8): 7, (4, 9): 16, (23, 28): 23}
        if len(most_common_tuples) == 1:
            del unique_date_matches[most_common_pattern][most_common_tuples[0]]
            for key in unique_date_matches[most_common_pattern].keys():
                if (
                    unique_date_matches[most_common_pattern][key]
                    > span_occurrences * 0.5
                ):
                    most_common_tuples.append(key)
                    logger.debug("Adding additional span: %s", key)
                    break
        logger.debug(
            "Most common pattern / tuples: %s",
            {most_common_pattern: most_common_tuples},
        )
        return {most_common_pattern: most_common_tuples}

    @staticmethod
    def get_items_with_same_page_and_line(items: list[DateMatch]) -> list[tuple]:
        """Groups date items with the same line and page number"""
        grouped_items: defaultdict[str, list] = defaultdict(list)
        for item in items:
            key = f"{item.page_number}-{item.line_number}"
            grouped_items[key].append(item.parsed_date)

        # Convert the dictionary into a list of tuples
        result = [(key, *values) for key, values in grouped_items.items()]
        return result

    def get_filtered_lines_with_dates(
        self, pattern_spans_mapping: dict
    ) -> list[DateMatch]:
        """
        Helper function to retrieve lines that are the most likely to contain
        transactions, based on the transaction pattern and spans from the
        `find_tuples_with_highest_occurrence()` function
        """
        pattern, spans = next(iter(pattern_spans_mapping.items()))
        filtered_lines_with_dates = []
        for line in self.patterns_with_date_matches[pattern]:
            if line.span in spans:
                filtered_lines_with_dates.append(line)

        if not filtered_lines_with_dates:
            raise ValueError(f"Span(s) {list(spans)} not found in lines")
        return filtered_lines_with_dates

    @lru_cache
    def is_transaction_date_first(self) -> bool:
        """
        Check that in cases where date_1 > date_2, the first date is
        identified as the posting date
        """
        # only focus on our main transaction pattern
        lines_with_multiple_dates = self.get_items_with_same_page_and_line(
            self.filtered_lines_with_dates
        )
        for line in lines_with_multiple_dates:
            logger.debug("Checking dates in line: %s", line)
            if len(line) > 2:
                _, date_1, date_2 = line
                if date_1 and date_2:
                    if date_1 != date_2:
                        logger.debug(
                            "%s != %s, returning %s", date_1, date_2, date_1 < date_2
                        )
                        return date_1 < date_2

        logger.warning(
            "Could not identify difference between transaction and posting date"
        )
        return True

    @lru_cache
    def create_transaction_pattern(
        self,
    ) -> str:
        """
        Create a regex pattern that will be used for date parsing
        by the generic statement handler.
        """
        pattern = next(iter(self.pattern_spans_mapping))
        logger.debug("Creating date pattern for %s", pattern)
        transaction_date_regex = self.date_regex_patterns[pattern].pattern
        date_regex = rf"(?P<transaction_date>{transaction_date_regex})\s+"
        spans = self.pattern_spans_mapping[pattern]

        if len(spans) > 2:
            raise ValueError("More than two date tuples found in statement")

        pattern = date_regex

        # if there are two spans, we attempt to determine which is the
        # posting date, and which is the transaction date
        if len(spans) == 2:
            logger.debug("Creating group for posting date")
            posting_date = f"(?P<posting_date>{transaction_date_regex})"
            if self.is_transaction_date_first():
                pattern = date_regex + rf"{posting_date}\s+"
            else:
                pattern = rf"{posting_date}\s+" + date_regex

        pattern += SharedPatterns.DESCRIPTION

        # if the statement is debit-type statement, we add the amount + balance patterns
        if self.get_statement_type() == EntryType.DEBIT:
            pattern += SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
            pattern += SharedPatterns.BALANCE

        if self.get_statement_type() == EntryType.CREDIT:
            pattern += SharedPatterns.AMOUNT_EXTENDED

        return pattern

    @lru_cache
    def create_statement_date_pattern(self) -> str:
        """
        Creates a regex pattern for the statement date based on the first statement
        date.
        """
        lines_with_yyyy_dates = {
            pattern: lines
            for pattern, lines in self.patterns_with_date_matches.items()
            if pattern.endswith("yy")
        }

        if not lines_with_yyyy_dates:
            raise RuntimeError(
                "No lines with `yy` or `yyyy` dates "
                "- unable to create statement date pattern"
            )

        # try yyyy patterns first before yy
        sorted_patterns = sorted(
            lines_with_yyyy_dates.keys(), key=lambda p: not p.endswith("yyyy")
        )

        unsorted_lines = []

        for pattern in sorted_patterns:
            lines = lines_with_yyyy_dates[pattern]
            for line in lines:
                unsorted_lines.append((pattern, line))

        sorted_lines: list[tuple[str, DateMatch]] = sorted(
            unsorted_lines, key=lambda x: (x[1].page_number, x[1].line_number)
        )

        _, date_match = sorted_lines[0]
        statement_date_pattern = f"({date_match.raw_date})"
        logger.debug("Found statement date pattern: %s", statement_date_pattern)

        # assume the statement date is the first parsable YYYY date
        return statement_date_pattern

    @lru_cache
    def get_statement_type(self) -> str:
        """
        Since debit and credit statements need to be handled differently,
        we use the average number of matches per line as a way to determine
        if a statement is a debit or credit statement.

        For example, a debit statement transaction line might be something like:
        `01 OCT   ValueVille    123.12     2,000.00`
        where the first number is either a deposit/withdrawal,
        and the next number is a balance.
        """
        # match up to amounts like `123.12     2,000.00` while ignoring words between
        amount_pattern = re.compile(
            r"(?P<amount>\d{1,3}(,\d{3})*(\.\d+)\d{1,3}(,\d{3})*(\.\d+)?)"
        )

        def get_num_amounts_per_line(lines: list[DateMatch]) -> float:
            matches = [
                result
                for line in lines
                for result in amount_pattern.finditer(line.line)
            ]
            return len(matches) / len(lines)

        average_matches_per_line = get_num_amounts_per_line(
            self.filtered_lines_with_dates
        )
        # this technically should be 1.0, but 1.1 provides some
        # slight tolerance for error
        if average_matches_per_line > 1.1:
            logger.debug(
                "Found %s amounts per line - assuming debit statement",
                average_matches_per_line,
            )
            return EntryType.DEBIT

        return EntryType.CREDIT

    @lru_cache
    def get_debit_statement_header_line(self) -> str:
        header_pattern = re.compile(r"\b(date.*$)", re.IGNORECASE)
        for line in self.lines_before_first_transaction:
            if line:
                # assume that the header always starts with `date` or `DATE`
                result = header_pattern.search(line)

                if result:
                    escaped_result = f"({re.escape(result.string)})"
                    logger.debug("Found header statement: %s", escaped_result)
                    return escaped_result

        raise RuntimeError("Could not find debit statement header line")

    @lru_cache
    def check_if_multiline(self) -> bool:
        """Checks if the statement should be treated as a multiline statement,
        where the description is split across multiple lines
        """
        line_numbers = [item.line_number for item in self.filtered_lines_with_dates]
        line_distance = [
            line_numbers[i] - line_numbers[i - 1] for i in range(1, len(line_numbers))
        ]
        # remove negative numbers, since this indicates that the transaction is
        # from the next page
        line_distance = [i for i in line_distance if i > 0]

        # if there's more than two lines between each transaction on average
        # we assume that this is a multiline statement
        average_line_distance = sum(line_distance) / len(line_distance)
        logger.debug(
            "Assuming multiline statement: average distance between transaction lines: %s",
            average_line_distance,
        )
        return average_line_distance > 2

    @lru_cache
    def create_previous_balance_regex(self) -> str | None:
        """Helper function to check for a previous balance line items.
        Makes the assumption that the previous balance line item, if it
        exists, will be the line before the first line item with a date.

        e.g.
        ```
        PREVIOUS BALANCE                       6,492.54
        05 OCT PAYMENT - DBS INTERNET/WIRELESS 6,492.54 CR
        ```
        """
        page_num, line_num = self.get_first_transaction_location()

        # grab the first five lines before the first transaction
        page = self.pages[page_num]
        lines_before_first_transaction = list(
            reversed(page.lines[line_num - 5 : line_num])
        )

        balance_pattern = re.compile(SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT)

        for line in lines_before_first_transaction:
            balance_match = balance_pattern.search(line)
            if balance_match:
                logger.debug("Balance match found")
                if word_match := re.search(r"(\b[a-zA-Z'\s]+)", balance_match.string):
                    words = word_match[0].strip()
                    pattern = (
                        SharedPatterns.DESCRIPTION.replace(".*?", words)
                        + SharedPatterns.AMOUNT
                    )
                    logger.debug("Found words, generated pattern %s", pattern)
                    return pattern
        return None

    @lru_cache
    def get_first_transaction_location(self):
        # uses the transaction pattern to find the first transaction
        pattern = re.compile(self.create_transaction_pattern(), re.IGNORECASE)

        for page_num, page in enumerate(self.pages):
            for line_num, line in enumerate(page.lines):
                match = pattern.search(line)
                if match:
                    logger.debug(
                        "Found first transaction at page %s line %s", page_num, line_num
                    )
                    return page_num, line_num
        raise RuntimeError("Could not find first transaction")
