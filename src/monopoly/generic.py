import logging
import re
from collections import defaultdict
from functools import cache

from dateparser import parse

from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)

date_regex_patterns = {
    "NUMERIC_ONLY": r"\b(\d{2}[\/\-]\d{2})",
    "NUMERIC_ONLY_YYYY": r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{4})",
    "PROPERCASE_DD_MMM": r"\b(\d{2}[-\s][A-Z]{1}[a-z]{2})",
    "PROPERCASE_DD_MMM_YYYY": r"\b(\d{2}[-\s][A-Z]{1}[a-z]{2}[-\s]\d{4})",
    "PROPERCASE_MMM_DDD": r"\b([A-Z]{1}[a-z]{2}[-\s]\d{2})",
    "PROPERCASE_MMM_DD_YYYY": r"\b([A-Z]{1}[a-z]{2}[-\s]\d{2}[-\s]\d{4})",
    "UPPERCASE_DD_MMM": r"\b(\d{2}[-\s][A-Z]{3})",
    "UPPERCASE_DD_MMM_YYYY": r"\b(\d{2}[-\s][A-Z]{3}[-\s]\d{4})",
    "UPPERCASE_MMM_DD": r"\b([A-Z]{3}[-\s]\d{2})",
    "UPPERCASE_MMM_DD_YYYY": r"\b([A-Z]{3}[-\s]\d{2}[-\s]\d{4})",
}


@cache
def compile_date_tuples(date_tuples: set[tuple]) -> set[tuple]:
    """Compile regex patterns for date matching and caches them"""
    return set(
        (pattern_name, re.compile(pattern)) for pattern_name, pattern in date_tuples
    )


def get_lines_with_date(
    date_tuples: list[tuple], pages: list[PdfPage]
) -> dict[str, list]:
    """Retrieves all possible transactions from every page, based on the assumption that
    a transaction line will always start with a date"""
    results: dict[str, list] = {}
    for date_tuple in date_tuples:
        pattern_name, pattern = date_tuple
        logger.debug("Searching for matches with %s", pattern_name)
        results[pattern_name] = []
        for page_num, page in enumerate(pages):
            for line_num, line in enumerate(page.lines):
                for date_match in re.finditer(pattern, line):
                    span = date_match.start(), date_match.end()
                    result = {
                        "span": span,
                        "value": date_match.group(),
                        "page_number": page_num,
                        "line_number": line_num,
                        "line": date_match.string,
                    }
                    # transactions should never be logged for data security reasons
                    logged_result = result.copy()
                    del logged_result["line"]
                    logger.debug("Match found: %s", logged_result)
                    results[pattern_name].append(result)
        # filter out patterns with no matches
        results = {key: value for key, value in results.items() if value}

    return results


def count_unique_date_matches(lines_with_date: dict[str, list]) -> dict:
    match_dict: dict = {}

    for pattern_name, matches in lines_with_date.items():
        match_dict[pattern_name] = {}

        unique_matches = set()
        for match in matches:
            unique_matches.add(match["span"])

        unique_matches = sorted(unique_matches)  # type: ignore

        for match in unique_matches:
            match_dict[pattern_name][match] = 0

        # count number of times each tuple occurs
        for match in matches:
            match_tuple = match["span"]
            if match_tuple in match_dict[pattern_name]:
                match_dict[pattern_name][match_tuple] += 1

    return match_dict


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
    """
    span_occurrences = 0
    most_common_pattern = None
    most_common_tuples = None

    for pattern, value in unique_date_matches.items():
        max_span_occurrences = max(value.values())

        if max_span_occurrences > span_occurrences:
            tuples = [k for k, v in value.items() if v == max_span_occurrences]
            span_occurrences = max_span_occurrences
            most_common_pattern = pattern
            most_common_tuples = tuples

    logger.debug(
        "Pattern %s matched %s times at span(s) %s",
        most_common_pattern,
        span_occurrences,
        most_common_tuples,
    )
    return {most_common_pattern: most_common_tuples}


def get_items_with_same_page_and_line(items: list[dict[str, list]]) -> list[tuple]:
    """Groups date items with the same line and page number"""
    grouped_items: defaultdict[str, list] = defaultdict(list)

    for item in items:
        page_number = item["page_number"]
        line_number = item["line_number"]
        key = f"{page_number}-{line_number}"
        grouped_items[key].append(item["value"])

    # Convert the dictionary into a list of tuples
    result = [(key, *values) for key, values in grouped_items.items()]

    return result


def get_filtered_lines_with_dates(
    lines_with_date: dict[str, list],
    transaction_pattern: str,
    transaction_spans: dict[tuple, int],
) -> list:
    """
    Helper function to retrieve lines that are the most likely to contain
    transactions, based on the transaction pattern and spans from the
    `find_tuples_with_highest_occurrence()` function
    """
    filtered_lines_with_dates = []
    for line in lines_with_date[transaction_pattern]:
        if line["span"] in transaction_spans:
            filtered_lines_with_dates.append(line)
    return filtered_lines_with_dates


def is_transaction_date_first(
    lines_with_date: dict[str, list], pattern_spans_mapping: dict[str, dict]
):
    """
    Check that in cases where date_1 > date_2, the first date is
    identified as the posting date
    """
    pattern, spans = next(iter(pattern_spans_mapping.items()))

    # only focus on our main transaction pattern
    filtered_lines_with_dates = get_filtered_lines_with_dates(
        lines_with_date, pattern, spans
    )

    if not filtered_lines_with_dates:
        raise ValueError(f"Span(s) {list(spans.keys())} not found in lines")

    lines_with_multiple_dates = get_items_with_same_page_and_line(
        filtered_lines_with_dates
    )
    for line in lines_with_multiple_dates:
        _, date_1, date_2 = line
        logger.debug(line)
        date_1 = parse(date_1)
        date_2 = parse(date_2)

        if date_1 and date_2:
            if date_1 != date_2:
                logger.debug("%s != %s, returning %s", date_1, date_2, date_1 < date_2)
                return date_1 < date_2

    logger.warning("Could not identify difference between transaction and posting date")
    return True


def create_date_regex_pattern(
    lines_with_date: dict[str, list],
    pattern_spans_mapping: dict,
):
    """
    Create a regex pattern that will be used for date parsing by the Generic parser.
    """
    pattern = next(iter(pattern_spans_mapping))
    logger.info("Creating date pattern for %s", pattern)
    transaction_date_regex = date_regex_patterns[pattern]
    date_regex = rf"(?P<transaction_date>{transaction_date_regex})\s+"

    if len(pattern_spans_mapping[pattern]) == 1:
        return date_regex

    if len(pattern_spans_mapping[pattern]) == 2:
        posting_date = f"(?P<posting_date>{transaction_date_regex})"
        if is_transaction_date_first(lines_with_date, pattern_spans_mapping):
            return date_regex + rf"{posting_date}\s+"
        return rf"{posting_date}\s+" + date_regex

    raise ValueError("More than two date tuples found in statement")


def create_statement_date_pattern(
    lines_with_date: dict[str, list],
):
    """
    Creates a regex pattern for the statement date based on the first statement date.
    This is technically redundant, since this means the parser will search for the
    statement date again, but this avoids having to create a processor override.
    """
    lines_with_yyyy_dates = {
        pattern: lines
        for pattern, lines in lines_with_date.items()
        if pattern.endswith("YYYY")
    }

    unsorted_lines = []
    for pattern, lines in lines_with_yyyy_dates.items():
        for line in lines:
            unsorted_lines.append((pattern, line))

    sorted_lines = sorted(
        unsorted_lines, key=lambda x: (x[1]["page_number"], x[1]["line_number"])
    )

    for pattern, line in sorted_lines:
        date = line["value"]
        parsed_date = parse(date)
        # assume the statement date is the first parsable YYYY date
        if parsed_date:
            logger.debug(
                "Found parsable date %s (%s) for pattern %s", date, parsed_date, pattern
            )
            return date_regex_patterns[pattern]
    raise ValueError("Unable to find statement date")
