import logging
import re
from collections import defaultdict
from functools import cached_property

from monopoly.constants import EntryType, SharedPatterns
from monopoly.pdf import MetadataIdentifier, PdfPage

from .patterns import DateMatch, DatePattern, PatternMatcher

logger = logging.getLogger(__name__)


DEBIT_MATCH_THRESHOLD = 1.1  # Avg matches per line above this are considered debit
EXPECTED_DATE_COUNT_PER_LINE = 2  # One transaction date + one posting date
EXPECTED_DATE_SPAN_COUNT = 2
MULTILINE_DISTANCE_THRESHOLD = 2  # Avg line gap above this is considered multiline


class GenericParserError(Exception):
    """Exception raised when the generic parser fails to find exceptions."""


class DatePatternAnalyzer:
    def __init__(self, pages: list[PdfPage], metadata: MetadataIdentifier):
        self.pages = pages
        self.matcher = PatternMatcher(pages)
        self.pattern: DatePattern = self.matcher.get_transaction_pattern()
        self.matches = self.pattern.matches
        self.spans = self.matcher.get_transaction_spans(self.pattern)
        self.metadata = metadata

    @cached_property
    def lines_before_first_transaction(self) -> list[str]:
        page_num, line_num = self.get_first_transaction_location()

        page = self.pages[page_num]

        # calculate the starting index, ensuring it's not negative
        start_index = max(line_num - 20, 0)
        lines_before_transaction = page.lines[start_index:line_num]
        return list(reversed(lines_before_transaction))

    def get_items_with_same_page_and_line(self) -> list[tuple]:
        """Group date items with the same line and page number."""
        grouped_items: defaultdict[str, list] = defaultdict(list)
        for match in self.matches:
            key = f"{match.page_number}-{match.line_number}"
            grouped_items[key].append(match.parsed_date)

        # Convert the dictionary into a list of tuple
        return [(key, *values) for key, values in grouped_items.items()]

    def is_transaction_date_first(self) -> bool:
        """Check that in cases where date_1 > date_2, the first date is identified as the posting date."""
        # only focus on our main transaction pattern
        lines_with_multiple_dates = self.get_items_with_same_page_and_line()
        for line in lines_with_multiple_dates:
            logger.debug("Checking dates in line: %s", line)
            if len(line) > EXPECTED_DATE_COUNT_PER_LINE:
                _, date_1, date_2 = line
                if date_1 and date_2 and date_1 != date_2:
                    logger.debug("%s != %s, returning %s", date_1, date_2, date_1 < date_2)
                    return date_1 < date_2

        logger.warning("Could not identify difference between transaction and posting date")
        return True

    def create_transaction_pattern(self) -> re.Pattern:
        """Create a regex pattern that will be used for date parsing by the generic statement handler."""
        logger.debug("Creating date pattern for %s", self.pattern.name)
        transaction_regex = rf"(?P<transaction_date>{self.pattern.regex})\s+"

        # if there are two spans, we attempt to determine which is the
        # posting date, and which is the transaction date
        if len(self.spans) == EXPECTED_DATE_SPAN_COUNT:
            logger.debug("Creating group for posting date")
            posting_regex = rf"(?P<posting_date>{self.pattern.regex})\s+"
            if self.is_transaction_date_first():
                pattern = transaction_regex + posting_regex
            else:
                pattern = posting_regex + transaction_regex
        else:
            pattern = transaction_regex

        pattern += SharedPatterns.DESCRIPTION

        # if the statement is debit-type statement, we add the amount + balance patterns
        if self.get_statement_type() == EntryType.DEBIT:
            pattern += SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
            pattern += SharedPatterns.BALANCE

        if self.get_statement_type() == EntryType.CREDIT:
            pattern += SharedPatterns.AMOUNT_EXTENDED

        return re.compile(pattern, re.IGNORECASE)

    def create_statement_date_pattern(self) -> re.Pattern:
        """Create a regex pattern for the statement date based on the first statement date."""
        statement_date = self.matcher.get_statement_date_pattern()
        return re.compile(f"({statement_date})")

    def get_statement_type(self) -> str:
        """
        Determine whether a statement is a debit or credit statement.

        Since debit and credit statements need to be handled differently,
        we use the average number of matches per line as a way to determine
        if a statement is a debit or credit statement.

        For example, a debit statement transaction line might be something like:
        `01 OCT   ValueVille    123.12     2,000.00`
        where the first number is either a deposit/withdrawal,
        and the next number is a balance.
        """
        # match up to amounts like `123.12     2,000.00` while ignoring words between
        amount_pattern = re.compile(r"(?P<amount>\d{1,3}(,\d{3})*(\.\d+)\d{1,3}(,\d{3})*(\.\d+)?)")

        def get_num_amounts_per_line(lines: list[DateMatch]) -> float:
            matches = [result for line in lines for result in amount_pattern.finditer(line.line)]
            return len(matches) / len(lines)

        average_matches_per_line = get_num_amounts_per_line(self.matches)
        # this technically should be 1.0, but 1.1 provides some
        # slight tolerance for error
        if average_matches_per_line > DEBIT_MATCH_THRESHOLD:
            logger.debug(
                "Found %s amounts per line - assuming debit statement",
                average_matches_per_line,
            )
            return EntryType.DEBIT

        return EntryType.CREDIT

    def get_debit_statement_header_line(self, lines_before_first_transaction) -> str:
        header_pattern = re.compile(r"\b(date.*$)", re.IGNORECASE)

        for line in lines_before_first_transaction:
            if line:
                # assume that the header always starts with `date` or `DATE`
                result = header_pattern.search(line)
                if result:
                    generalized_result = re.sub(r"\s{3,}", r"\\s+", result.string)
                    escaped_result = re.escape(generalized_result)
                    escaped_result = escaped_result.replace("\\\\s\\+", r"\s+")
                    logger.debug("Found header statement: %s", escaped_result)
                    return escaped_result

        msg = "Could not find debit statement header line"
        raise RuntimeError(msg)

    def check_if_multiline(self) -> bool:
        """Check if the statement should be treated as a multiline statement."""
        line_numbers = [item.line_number for item in self.matches]
        line_distance = [line_numbers[i] - line_numbers[i - 1] for i in range(1, len(line_numbers))]
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
        return average_line_distance > MULTILINE_DISTANCE_THRESHOLD

    def create_previous_balance_regex(self) -> re.Pattern | None:
        """
        Check for a previous balance line items.

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
        lines_before_first_transaction = list(reversed(page.lines[line_num - 5 : line_num]))

        balance_pattern = re.compile(SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT)

        for line in lines_before_first_transaction:
            balance_match = balance_pattern.search(line)
            if balance_match:
                logger.debug("Balance match found")
                if word_match := re.search(r"(\b[a-zA-Z'\s]+)", balance_match.string):
                    words = word_match[0].strip()
                    pattern = SharedPatterns.DESCRIPTION.replace(".*?", words) + SharedPatterns.AMOUNT
                    logger.debug("Found words, generated pattern %s", pattern)
                    return re.compile(pattern)
        return None

    def get_first_transaction_location(self):
        # uses the transaction pattern to find the first transaction
        pattern = self.create_transaction_pattern()

        for page_num, page in enumerate(self.pages):
            for line_num, line in enumerate(page.lines):
                match = pattern.search(line)
                if match:
                    logger.debug("Found first transaction at page %s line %s", page_num, line_num)
                    return page_num, line_num
        msg = f"Could not find any transactions. PDF metadata: {self.metadata})"
        raise GenericParserError(msg)
