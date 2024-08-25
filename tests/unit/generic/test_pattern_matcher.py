from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from monopoly.generic.patterns import DateMatch, DatePattern, PatternMatcher
from monopoly.pdf import PdfPage


@pytest.fixture(scope="session")
def mock_pages():
    pages = [
        PdfPage("                Statement Date   31 Oct 2024"),
        PdfPage("01 Oct   ValueVille   123.12 \n02 Oct   RandomShop 124.50"),
        PdfPage("04 Oct   Fernvale Food   12.12\nPayment Due Date   21 Aug 2024"),
    ]
    yield pages


@pytest.fixture(scope="function")
def pattern_matcher(mock_pages):
    yield PatternMatcher(pages=mock_pages)


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


def test_pattern_matcher(pattern_matcher: PatternMatcher):
    pattern: DatePattern = pattern_matcher.get_transaction_pattern()
    spans = pattern_matcher.get_transaction_spans(pattern)

    assert spans == {(0, 6)}
    assert len([pattern for pattern in pattern_matcher]) == 8
    assert pattern.name == "dd_mmm"
    assert pattern.span_occurrences == Counter({(0, 6): 3, (33, 39): 1, (19, 25): 1})
    assert pattern.unique_spans == {(19, 25), (0, 6), (33, 39)}
    assert pattern.matched_lines == [
        "                Statement Date   31 Oct 2024",
        "01 Oct   ValueVille   123.12 ",
        "02 Oct   RandomShop 124.50",
        "04 Oct   Fernvale Food   12.12",
        "Payment Due Date   21 Aug 2024",
    ]


def test_get_transaction_pattern():
    pattern1 = MagicMock(spec=DatePattern)
    pattern1.name = "dd_mmm"
    pattern1.span_occurrences = Counter({(0, 6): 3, (33, 39): 1})

    pattern2 = MagicMock(spec=DatePattern)
    pattern2.name = "dd_mm"
    pattern2.span_occurrences = Counter({(1, 7): 12, (11, 17): 12, (33, 39): 1})

    pattern3 = MagicMock(spec=DatePattern)
    pattern3.name = "mmm_dd"
    pattern3.span_occurrences = Counter({(0, 5): 2})

    with patch.object(PatternMatcher, "set_date_patterns", return_value=None):
        pattern_matcher = PatternMatcher(pages=[])

        pattern_matcher.dd_mmm = pattern1
        pattern_matcher.dd_mmm_yy = pattern2
        pattern_matcher.mmm_dd = pattern3
        pattern = pattern_matcher.get_transaction_pattern()
        spans = pattern_matcher.get_transaction_spans(pattern)
        assert pattern.name == "dd_mm"
        assert spans == {(1, 7), (11, 17)}
