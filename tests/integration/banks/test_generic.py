import logging
import re

import pytest

from monopoly.generic import (
    compile_date_tuples,
    count_unique_date_matches,
    create_date_regex_pattern,
    create_statement_date_pattern,
    date_regex_patterns,
    find_tuples_with_highest_occurrence,
    get_filtered_lines_with_dates,
    get_items_with_same_page_and_line,
    get_lines_with_date,
    is_transaction_date_first,
)
from monopoly.pdf import PdfPage


@pytest.fixture(scope="session")
def date_regex_set():
    return frozenset(date_regex_patterns.items())


@pytest.fixture(scope="session")
def mock_pages():
    pages = [
        PdfPage("                Statement Date   31 Oct 2024"),
        PdfPage("01 Oct   ValueVille   123.12 \n02 Oct   RandomShop 124.50"),
        PdfPage("04 Oct   Fernvale Food   12.12"),
    ]
    return pages


@pytest.fixture(scope="session")
def lines_with_date():
    return {
        "PROPERCASE_MMM_DDD": [
            {
                "span": (36, 42),
                "value": "Oct 20",
                "page_number": 0,
                "line_number": 0,
                "line": "                Statement Date   31 Oct 2024",
            }
        ],
        "PROPERCASE_DD_MMM": [
            {
                "span": (33, 39),
                "value": "31 Oct",
                "page_number": 0,
                "line_number": 0,
                "line": "                Statement Date   31 Oct 2024",
            },
            {
                "span": (0, 6),
                "value": "01 Oct",
                "page_number": 1,
                "line_number": 0,
                "line": "01 Oct   ValueVille   123.12 ",
            },
            {
                "span": (0, 6),
                "value": "02 Oct",
                "page_number": 1,
                "line_number": 1,
                "line": "02 Oct   RandomShop 124.50",
            },
            {
                "span": (0, 6),
                "value": "04 Oct",
                "page_number": 2,
                "line_number": 0,
                "line": "04 Oct   Fernvale Food   12.12",
            },
        ],
        "PROPERCASE_DD_MMM_YYYY": [
            {
                "span": (33, 44),
                "value": "31 Oct 2024",
                "page_number": 0,
                "line_number": 0,
                "line": "                Statement Date   31 Oct 2024",
            }
        ],
    }


@pytest.fixture(scope="session")
def lines_with_transaction_posting_dates():
    return {
        "UPPERCASE_DD_MMM": [
            {
                "span": (10, 16),
                "value": "03 OCT",
                "page_number": 0,
                "line_number": 31,
                "line": "  03 OCT           03 OCT           FAST PAYMENT  1.90",
            },
            {
                "span": (27, 33),
                "value": "03 OCT",
                "page_number": 0,
                "line_number": 31,
                "line": "  03 OCT           03 OCT           FAST PAYMENT   1.90",
            },
            {
                "span": (10, 16),
                "value": "04 OCT",
                "page_number": 0,
                "line_number": 36,
                "line": "  04 OCT           04 OCT           BILL PAYMENT   123.12",
            },
            {
                "span": (27, 33),
                "value": "05 OCT",
                "page_number": 0,
                "line_number": 36,
                "line": "  04 OCT           05 OCT           BILL PAYMENT   123.12",
            },
        ]
    }


@pytest.fixture(scope="session")
def lines_with_posting_transaction_dates():
    return {
        "UPPERCASE_DD_MMM": [
            {
                "span": (10, 16),
                "value": "05 OCT",
                "page_number": 0,
                "line_number": 36,
                "line": "  05 OCT           04 OCT           BILL PAYMENT   123.12",
            },
            {
                "span": (27, 33),
                "value": "04 OCT",
                "page_number": 0,
                "line_number": 36,
                "line": "  05 OCT           04 OCT           BILL PAYMENT   123.12",
            },
        ]
    }


def test_compile_date_tuples(date_regex_set):
    expected = [
        ("PROPERCASE_DD_MMM", re.compile(r"\b(\d{2}[-\s][A-Z]{1}[a-z]{2})")),
        ("UPPERCASE_DD_MMM", re.compile(r"\b(\d{2}[-\s][A-Z]{3})")),
    ]
    results = compile_date_tuples(date_regex_set)
    for item in expected:
        assert item in results


def test_get_lines_with_date(
    date_regex_set, mock_pages, lines_with_date, caplog: pytest.LogCaptureFixture
):
    caplog.set_level(logging.DEBUG)
    expected = lines_with_date
    result = get_lines_with_date(date_regex_set, mock_pages)
    assert expected == result
    for values in result.values():

        # also check that transactions aren"t being logged for data security reasons
        for value in values:
            assert value["line"] not in caplog.text


def test_count_unique_date_matches(
    lines_with_date, lines_with_transaction_posting_dates
):
    assert count_unique_date_matches(lines_with_date) == {
        "PROPERCASE_MMM_DDD": {(36, 42): 1},
        "PROPERCASE_DD_MMM": {(0, 6): 3, (33, 39): 1},
        "PROPERCASE_DD_MMM_YYYY": {(33, 44): 1},
    }
    assert count_unique_date_matches(lines_with_transaction_posting_dates) == {
        "UPPERCASE_DD_MMM": {(10, 16): 2, (27, 33): 2}
    }


def test_find_tuples_with_highest_occurrence():
    single_match = {"PROPERCASE_DD_MMM": {(0, 6): 3, (33, 39): 1}}
    double_match = {"UPPERCASE_DD_MMM": {(1, 7): 12, (11, 17): 12, (33, 39): 1}}
    assert find_tuples_with_highest_occurrence(single_match) == {
        "PROPERCASE_DD_MMM": [(0, 6)]
    }
    assert find_tuples_with_highest_occurrence(double_match) == {
        "UPPERCASE_DD_MMM": [(1, 7), (11, 17)]
    }


def test_identify_transaction_date_with_improper_spans(
    lines_with_transaction_posting_dates,
):
    pattern_spans_mapping = {"UPPERCASE_DD_MMM": {(0, 6): 3}}
    with pytest.raises(ValueError, match="not found in lines"):
        is_transaction_date_first(
            lines_with_transaction_posting_dates, pattern_spans_mapping
        )


def test_identify_transaction_date(lines_with_transaction_posting_dates):
    pattern_spans_mapping = {"UPPERCASE_DD_MMM": {(10, 16): 2, (27, 33): 2}}
    result = is_transaction_date_first(
        lines_with_transaction_posting_dates, pattern_spans_mapping
    )
    assert result


def test_identify_posting_date(lines_with_posting_transaction_dates):
    """Check that in cases where date_1 > date_2, the first date is identified
    as the posting date"""
    transaction_date_dict = {"UPPERCASE_DD_MMM": {(10, 16): 2, (27, 33): 2}}
    result = is_transaction_date_first(
        lines_with_posting_transaction_dates, transaction_date_dict
    )
    assert not result


def test_create_date_regex_pattern(
    lines_with_transaction_posting_dates,
    lines_with_posting_transaction_dates,
):
    pattern_spans_mapping = {"UPPERCASE_DD_MMM": {(10, 16): 2, (27, 33): 2}}

    expected = (
        "(?P<transaction_date>\\b(\\d{2}[-\\s][A-Z]{3}))"
        + "\\s+(?P<posting_date>\\b(\\d{2}[-\\s][A-Z]{3}))\\s+"
    )
    result = create_date_regex_pattern(
        lines_with_transaction_posting_dates, pattern_spans_mapping
    )
    assert result == expected

    expected = (
        "(?P<posting_date>\\b(\\d{2}[-\\s][A-Z]{3}))"
        + "\\s+(?P<transaction_date>\\b(\\d{2}[-\\s][A-Z]{3}))\\s+"
    )
    result = create_date_regex_pattern(
        lines_with_posting_transaction_dates, pattern_spans_mapping
    )
    assert result == expected


def test_get_items_with_same_page_line():
    lines_with_multiple_dates = [
        {"span": (10, 16), "value": "03 OCT", "page_number": 0, "line_number": 36},
        {"span": (27, 33), "value": "04 OCT", "page_number": 0, "line_number": 36},
        {"span": (10, 16), "value": "05 OCT", "page_number": 1, "line_number": 10},
        {"span": (27, 33), "value": "06 OCT", "page_number": 1, "line_number": 10},
    ]
    expected = [("0-36", "03 OCT", "04 OCT"), ("1-10", "05 OCT", "06 OCT")]
    assert get_items_with_same_page_and_line(lines_with_multiple_dates) == expected


def test_create_statement_date_pattern(
    lines_with_date, caplog: pytest.LogCaptureFixture
):
    caplog.set_level(logging.DEBUG)
    expected = "\\b(\\d{2}[-\\s][A-Z]{1}[a-z]{2}[-\\s]\\d{4})"
    assert create_statement_date_pattern(lines_with_date) == expected
    expected_logs = ["parsable date 31 Oct 2024", "PROPERCASE_DD_MMM_YYYY"]
    for log in expected_logs:
        assert log in caplog.text


def test_get_filtered_lines_with_dates():
    lines_with_date = {
        "pattern1": [
            {"line": "01 OCT  ValueVille  123.12  2,000.00", "span": (0, 4)},
            {"line": "02 OCT  ShopMart    50.00   1,950.00", "span": (5, 9)},
            {"line": "03 OCT  CafeCafe    5.50    1,944.50", "span": (10, 14)},
        ],
        "pattern2": [
            {"line": "01 NOV  Market    100.00  2,100.00", "span": (0, 4)},
            {"line": "02 NOV  Deli      25.00   2,075.00", "span": (5, 9)},
            {"line": "03 NOV  Store     30.00   2,045.00", "span": (10, 14)},
        ],
    }

    transaction_pattern = "pattern1"
    transaction_spans = [(0, 4), (10, 14)]

    expected_output = [
        {"line": "01 OCT  ValueVille  123.12  2,000.00", "span": (0, 4)},
        {"line": "03 OCT  CafeCafe    5.50    1,944.50", "span": (10, 14)},
    ]

    result = get_filtered_lines_with_dates(
        lines_with_date, transaction_pattern, transaction_spans
    )
    assert result == expected_output
