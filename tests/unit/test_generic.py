import logging
import re
from dataclasses import dataclass
from datetime import datetime

import pytest

from monopoly.constants import DateFormats, DateRegexPatterns, EntryType, SharedPatterns
from monopoly.generic import DateMatch, DatePatternAnalyzer
from monopoly.pdf import PdfPage


@pytest.fixture(scope="function")
def date_pattern_analyzer(mock_pages) -> DatePatternAnalyzer:
    dpa = DatePatternAnalyzer(pages=mock_pages)
    yield dpa


@pytest.fixture(scope="session")
def date_regex_set():
    yield frozenset(DateRegexPatterns())


@pytest.fixture(scope="session")
def mock_pages():
    pages = [
        PdfPage("                Statement Date   31 Oct 2024"),
        PdfPage("01 Oct   ValueVille   123.12 \n02 Oct   RandomShop 124.50"),
        PdfPage("04 Oct   Fernvale Food   12.12\nPayment Due Date   21 Aug 2024"),
    ]
    yield pages


@pytest.fixture(scope="session")
def lines_before_first_transaction():
    yield list(
        reversed(
            [
                "DBS Bank Ltd",
                "12 Marina Boulevard, Marina Bay Financial Centre Tower 3, Singapore 018982",
                "www.dbs.com",
                "123123123-1234",
                "                JOHN",
                "                FUBAR",
                "                3 STARLING DRIVE",
                "                #01-01 THOMSON RESIDENCES",
                "                SINGAPORE 123456",
                "                                                       As at 31 Oct 2023",
                "",
                " Details of Your DBS Debit Account                     Account No.: 123-4-56789",
                "",
                " DATE    DETAILS OF TRANSACTIONS     WITHDRAWAL($)    DEPOSIT($)     BALANCE($)",
                "",
                "                          Balance Brought Forward                        222.13",
            ]
        )
    )


@dataclass
class MockDateMatch(DateMatch):
    span: tuple[int, int] = (0, 0)
    line: str = ""
    parsed_date: datetime = datetime(1970, 1, 1)
    raw_date: str = ""
    line_number: int = 0
    page_number: int = 0


@pytest.fixture(scope="session")
def patterns_with_date_matches():
    return {
        "dd_mmm": [
            DateMatch(
                span=(33, 39),
                parsed_date=datetime(2024, 10, 31, 0, 0),
                raw_date="31 Oct",
                page_number=0,
                line_number=0,
                line="                Statement Date   31 Oct 2024",
            ),
            DateMatch(
                span=(0, 6),
                parsed_date=datetime(2024, 10, 1, 0, 0),
                raw_date="01 Oct",
                page_number=1,
                line_number=0,
                line="01 Oct   ValueVille   123.12 ",
            ),
            DateMatch(
                span=(0, 6),
                parsed_date=datetime(2024, 10, 2, 0, 0),
                raw_date="02 Oct",
                page_number=1,
                line_number=1,
                line="02 Oct   RandomShop 124.50",
            ),
            DateMatch(
                span=(0, 6),
                parsed_date=datetime(2024, 10, 4, 0, 0),
                raw_date="04 Oct",
                page_number=2,
                line_number=0,
                line="04 Oct   Fernvale Food   12.12",
            ),
            DateMatch(
                span=(19, 25),
                parsed_date=datetime(2024, 8, 21, 0, 0),
                raw_date="21 Aug",
                page_number=2,
                line_number=1,
                line="Payment Due Date   21 Aug 2024",
            ),
        ],
        "dd_mmm_yyyy": [
            DateMatch(
                span=(33, 44),
                parsed_date=datetime(2024, 10, 31, 0, 0),
                raw_date="31 Oct 2024",
                page_number=0,
                line_number=0,
                line="                Statement Date   31 Oct 2024",
            ),
            DateMatch(
                span=(19, 30),
                parsed_date=datetime(2024, 8, 21, 0, 0),
                raw_date="21 Aug 2024",
                page_number=2,
                line_number=1,
                line="Payment Due Date   21 Aug 2024",
            ),
        ],
        "mmm_dd": [
            DateMatch(
                span=(
                    36,
                    42,
                ),
                parsed_date=datetime(2024, 10, 20, 0, 0),
                raw_date="Oct 20",
                page_number=0,
                line_number=0,
                line="                Statement Date   31 Oct 2024",
            ),
            DateMatch(
                span=(
                    22,
                    28,
                ),
                parsed_date=datetime(2024, 8, 20, 0, 0),
                raw_date="Aug 20",
                page_number=2,
                line_number=1,
                line="Payment Due Date   21 Aug 2024",
            ),
        ],
    }


@pytest.fixture(scope="session")
def lines_with_transaction_posting_dates():
    yield {
        "dd_mmm": [
            MockDateMatch(
                span=(10, 16),
                raw_date="03 OCT",
                parsed_date=datetime(2024, 10, 3),
                page_number=0,
                line_number=31,
                line="  03 OCT           03 OCT           FAST PAYMENT  1.90",
            ),
            MockDateMatch(
                span=(27, 33),
                raw_date="03 OCT",
                parsed_date=datetime(2024, 10, 3),
                page_number=0,
                line_number=31,
                line="  03 OCT           03 OCT           FAST PAYMENT   1.90",
            ),
            MockDateMatch(
                span=(10, 16),
                raw_date="04 OCT",
                parsed_date=datetime(2024, 10, 4),
                page_number=0,
                line_number=36,
                line="  04 OCT           04 OCT           BILL PAYMENT   123.12",
            ),
            MockDateMatch(
                span=(27, 33),
                raw_date="05 OCT",
                parsed_date=datetime(2024, 10, 5),
                page_number=0,
                line_number=36,
                line="  04 OCT           05 OCT           BILL PAYMENT   123.12",
            ),
        ]
    }


@pytest.fixture(scope="session")
def lines_with_posting_transaction_dates():
    yield {
        "dd_mmm": [
            MockDateMatch(
                span=(10, 16),
                raw_date="05 OCT",
                parsed_date=datetime(2024, 10, 5),
                page_number=0,
                line_number=36,
                line="  05 OCT           04 OCT           BILL PAYMENT   123.12",
            ),
            MockDateMatch(
                span=(27, 33),
                raw_date="04 OCT",
                parsed_date=datetime(2024, 10, 4),
                page_number=0,
                line_number=36,
                line="  05 OCT           04 OCT           BILL PAYMENT   123.12",
            ),
        ]
    }


def test_get_patterns_with_date_matches(
    date_pattern_analyzer: DatePatternAnalyzer,
    patterns_with_date_matches,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.DEBUG)
    expected = patterns_with_date_matches
    result = date_pattern_analyzer.get_patterns_with_date_matches()

    assert expected == result


def test_count_unique_date_matches(
    date_pattern_analyzer: DatePatternAnalyzer,
    lines_with_transaction_posting_dates,
):
    assert date_pattern_analyzer.count_unique_date_matches() == {
        "dd_mmm": {(0, 6): 3, (19, 25): 1, (33, 39): 1},
        "dd_mmm_yyyy": {(19, 30): 1, (33, 44): 1},
        "mmm_dd": {(22, 28): 1, (36, 42): 1},
    }
    date_pattern_analyzer.patterns_with_date_matches = (
        lines_with_transaction_posting_dates
    )
    assert date_pattern_analyzer.count_unique_date_matches() == {
        "dd_mmm": {(10, 16): 2, (27, 33): 2}
    }


def test_find_tuples_with_highest_occurrence(
    date_pattern_analyzer: DatePatternAnalyzer,
):
    single_match = {"dd_mmm": {(0, 6): 3, (33, 39): 1}}
    double_match = {"dd_mmm": {(1, 7): 12, (11, 17): 12, (33, 39): 1}}
    assert date_pattern_analyzer.find_tuples_with_highest_occurrence(single_match) == {
        "dd_mmm": [(0, 6)]
    }
    assert date_pattern_analyzer.find_tuples_with_highest_occurrence(double_match) == {
        "dd_mmm": [(1, 7), (11, 17)]
    }


def test_identify_transaction_date(
    date_pattern_analyzer: DatePatternAnalyzer, lines_with_transaction_posting_dates
):
    date_pattern_analyzer.patterns_with_date_matches = (
        lines_with_transaction_posting_dates
    )
    date_pattern_analyzer.filtered_lines_with_dates = (
        lines_with_transaction_posting_dates["dd_mmm"]
    )
    result = date_pattern_analyzer.is_transaction_date_first()
    assert result


def test_identify_posting_date(
    date_pattern_analyzer: DatePatternAnalyzer, lines_with_posting_transaction_dates
):
    """Check that in cases where date_1 > date_2, the first date is identified
    as the posting date"""
    date_pattern_analyzer.patterns_with_date_matches = (
        lines_with_posting_transaction_dates
    )
    date_pattern_analyzer.filtered_lines_with_dates = (
        lines_with_posting_transaction_dates["dd_mmm"]
    )
    result = date_pattern_analyzer.is_transaction_date_first()
    assert not result


def test_create_transaction_pattern_with_transaction_first(
    date_pattern_analyzer: DatePatternAnalyzer,
    lines_with_transaction_posting_dates,
):
    expected = (
        f"(?P<transaction_date>\\b({DateFormats.DD}"
        f"[-\\s]{DateFormats.MMM}))\\s+"
        f"(?P<posting_date>\\b({DateFormats.DD}"
        f"[-\\s]{DateFormats.MMM}))\\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    date_pattern_analyzer.patterns_with_date_matches = (
        lines_with_transaction_posting_dates
    )
    date_pattern_analyzer.filtered_lines_with_dates = (
        lines_with_transaction_posting_dates["dd_mmm"]
    )
    date_pattern_analyzer.pattern_spans_mapping = {"dd_mmm": {(10, 16): 2, (27, 33): 2}}

    result = date_pattern_analyzer.create_transaction_pattern()
    assert result == expected


def test_create_transaction_pattern_with_posting_first(
    date_pattern_analyzer: DatePatternAnalyzer,
    lines_with_posting_transaction_dates,
):
    date_pattern_analyzer.filtered_lines_with_dates = (
        lines_with_posting_transaction_dates["dd_mmm"]
    )
    date_pattern_analyzer.patterns_with_date_matches = (
        lines_with_posting_transaction_dates
    )
    date_pattern_analyzer.pattern_spans_mapping = {"dd_mmm": {(10, 16): 2, (27, 33): 2}}

    expected = (
        f"(?P<posting_date>\\b({DateFormats.DD}"
        f"[-\\s]{DateFormats.MMM}))\\s+"
        f"(?P<transaction_date>\\b({DateFormats.DD}"
        f"[-\\s]{DateFormats.MMM}))\\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    result = date_pattern_analyzer.create_transaction_pattern()
    assert result == expected


def test_get_items_with_same_page_line(date_pattern_analyzer: DatePatternAnalyzer):
    lines_with_multiple_dates = [
        MockDateMatch(
            span=(10, 16),
            raw_date="03 OCT",
            parsed_date=datetime(2024, 10, 3),
            page_number=0,
            line_number=36,
        ),
        MockDateMatch(
            span=(27, 33),
            raw_date="04 OCT",
            parsed_date=datetime(2024, 10, 4),
            page_number=0,
            line_number=36,
        ),
        MockDateMatch(
            span=(10, 16),
            raw_date="05 OCT",
            parsed_date=datetime(2024, 10, 5),
            page_number=1,
            line_number=10,
        ),
        MockDateMatch(
            span=(27, 33),
            raw_date="06 OCT",
            parsed_date=datetime(2024, 10, 6),
            page_number=1,
            line_number=10,
        ),
    ]
    expected = [
        ("0-36", datetime(2024, 10, 3), datetime(2024, 10, 4)),
        ("1-10", datetime(2024, 10, 5), datetime(2024, 10, 6)),
    ]
    assert (
        date_pattern_analyzer.get_items_with_same_page_and_line(
            lines_with_multiple_dates
        )
        == expected
    )


def test_create_statement_date_pattern(
    date_pattern_analyzer: DatePatternAnalyzer,
    patterns_with_date_matches,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.DEBUG)
    expected = "(31 Oct 2024)"
    date_pattern_analyzer.patterns_with_date_matches = patterns_with_date_matches
    assert date_pattern_analyzer.create_statement_date_pattern() == expected


def test_get_filtered_lines_with_dates(date_pattern_analyzer: DatePatternAnalyzer):
    patterns_with_date_matches = {
        "pattern1": [
            MockDateMatch(line="01 OCT  ValueVille  123.12  2,000.00", span=(0, 4)),
            MockDateMatch(line="99 Ref", span=(5, 9)),
            MockDateMatch(line="03 OCT  CafeCafe    5.50    1,944.50", span=(10, 14)),
        ],
        "pattern2": ["foo", "bar", "baz"],
    }
    date_pattern_analyzer.patterns_with_date_matches = patterns_with_date_matches
    pattern_spans_mapping = {"pattern1": {(0, 4): 1, (10, 14): 1}}

    expected_output = [
        MockDateMatch(line="01 OCT  ValueVille  123.12  2,000.00", span=(0, 4)),
        MockDateMatch(line="03 OCT  CafeCafe    5.50    1,944.50", span=(10, 14)),
    ]
    result = date_pattern_analyzer.get_filtered_lines_with_dates(pattern_spans_mapping)
    assert result == expected_output


def test_get_statement_type_debit(date_pattern_analyzer: DatePatternAnalyzer):
    debit_lines = [
        MockDateMatch(line="01 OCT   ValueVille    123.12     2,000.00"),
        MockDateMatch(line="02 OCT   ShopMart      50.00      1,950.00"),
        MockDateMatch(line="03 OCT   CafeCafe      5.50       1,944.50"),
    ]
    date_pattern_analyzer.filtered_lines_with_dates = debit_lines
    assert date_pattern_analyzer.get_statement_type() == EntryType.DEBIT


def test_get_statement_type_credit(date_pattern_analyzer: DatePatternAnalyzer):
    credit_lines = [
        MockDateMatch(line="01 OCT   Payment received    1,000.00"),
        MockDateMatch(line="02 OCT   Payment received    1,200.00"),
        MockDateMatch(line="03 OCT   Payment received    1,300.00"),
    ]
    date_pattern_analyzer.filtered_lines_with_dates = credit_lines
    assert date_pattern_analyzer.get_statement_type() == EntryType.CREDIT


def test_get_statement_type_mixed_debit(date_pattern_analyzer: DatePatternAnalyzer):
    mixed_debit_lines = [
        MockDateMatch(line="01 OCT   ValueVille          123.12     2,000.00"),
        MockDateMatch(line="02 OCT   Payment received               1,000.00"),
        MockDateMatch(line="03 OCT   CafeCafe            5.50       1,944.50"),
        MockDateMatch(line="04 OCT   Funds Transfer      20.00      1,924.50"),
    ]
    date_pattern_analyzer.filtered_lines_with_dates = mixed_debit_lines
    assert date_pattern_analyzer.get_statement_type() == EntryType.DEBIT


def test_get_debit_statement_header_line(
    lines_before_first_transaction, date_pattern_analyzer: DatePatternAnalyzer
):
    class MockPdfPage:
        def __init__(self, lines):
            self.lines = lines

    pages = [MockPdfPage(lines_before_first_transaction)]
    filtered_lines_with_dates = [MockDateMatch(line_number=22, page_number=0)]
    date_pattern_analyzer.pages = pages
    date_pattern_analyzer.filtered_lines_with_dates = filtered_lines_with_dates
    expected_header = re.escape(
        " DATE    DETAILS OF TRANSACTIONS     WITHDRAWAL($)    DEPOSIT($)     BALANCE($)"
    )
    result = date_pattern_analyzer.get_debit_statement_header_line()
    assert result == f"({expected_header})"


def test_check_if_multiline(date_pattern_analyzer: DatePatternAnalyzer):
    mulitline_statement_lines = [
        MockDateMatch(page_number=0, line_number=57),
        MockDateMatch(page_number=0, line_number=61),
        MockDateMatch(page_number=0, line_number=67),
        MockDateMatch(page_number=0, line_number=73),
        MockDateMatch(page_number=0, line_number=79),
        MockDateMatch(page_number=1, line_number=18),
        MockDateMatch(page_number=1, line_number=24),
        MockDateMatch(page_number=1, line_number=28),
        MockDateMatch(page_number=1, line_number=34),
        MockDateMatch(page_number=1, line_number=40),
    ]
    date_pattern_analyzer.filtered_lines_with_dates = mulitline_statement_lines
    assert date_pattern_analyzer.check_if_multiline()


def test_check_if_not_multiline(date_pattern_analyzer: DatePatternAnalyzer):
    single_lines = [
        MockDateMatch(page_number=0, line_number=57),
        MockDateMatch(page_number=0, line_number=58),
        MockDateMatch(page_number=1, line_number=21),
        MockDateMatch(page_number=1, line_number=22),
        MockDateMatch(page_number=1, line_number=23),
    ]
    date_pattern_analyzer.filtered_lines_with_dates = single_lines
    assert not date_pattern_analyzer.check_if_multiline()


def test_create_previous_balance_regex(
    lines_before_first_transaction, date_pattern_analyzer: DatePatternAnalyzer
):
    date_pattern_analyzer.lines_before_first_transaction = (
        lines_before_first_transaction
    )
    expected = rf"(?P<description>Balance Brought Forward)\s+{SharedPatterns.AMOUNT}"
    result = date_pattern_analyzer.create_previous_balance_regex()
    expected == result


@pytest.mark.parametrize(
    "date_format, valid_dates",
    [
        ("dd_mm", ["01/01", "15-05", "31/12"]),
        ("dd_mm_yy", ["01-01-20", "31/12/24", "15/05/30"]),
        ("dd_mmm", ["01 JAN", "15 FEB", "31 MAR"]),
        ("dd_mmm_yyyy", ["01 JAN 2023", "15 Feb 2024", "31 mar, 2025"]),
        ("dd_mm_yyyy", ["01/01/2023", "15-05-2024", "31/12/2025"]),
        ("mmmm_dd_yyyy", ["January 01, 2023", "FEBRUARY 15, 2024", "MARCH 31 2025"]),
        ("mmm_dd", ["JAN 01", "Feb 15", "MAR 31"]),
        ("mmm_dd_yyyy", ["JAN 01, 2023", "Feb 15, 2024", "MAR 31 2025"]),
    ],
)
def test_date_formats(
    date_pattern_analyzer: DatePatternAnalyzer, date_format: str, valid_dates
):
    patterns = date_pattern_analyzer.date_regex_patterns
    for date in valid_dates:
        assert patterns[date_format].match(date)
