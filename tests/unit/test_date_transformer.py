import re
from datetime import datetime

import pytest

from monopoly.config import DateOrder, StatementConfig
from monopoly.constants import EntryType
from monopoly.statements.date_transformer import DateTransformer


def _transformer(statement_date: datetime, date_format: str = "%d %b", order: str = "DMY") -> DateTransformer:
    config = StatementConfig(
        statement_type=EntryType.CREDIT,
        transaction_pattern=re.compile("foo"),
        statement_date_pattern=re.compile("bar"),
        header_pattern=re.compile("baz"),
        transaction_date_format=date_format,
        transaction_date_order=DateOrder(order),
    )
    return DateTransformer(config, statement_date)


class TestYearInjection:
    def test_year_is_taken_from_the_statement_date(self):
        transformer = _transformer(datetime(2023, 7, 15))
        assert transformer.to_iso8601("04 Aug") == "2023-08-04"

    def test_a_date_that_already_has_a_year_is_left_alone(self):
        transformer = _transformer(datetime(2023, 7, 15), date_format="%d %b %Y")
        assert transformer.to_iso8601("04 Aug 2021") == "2021-08-04"


class TestCrossYear:
    """
    A Jan/Feb statement still lists the prior December's transactions.

    Naively taking the year from the statement date would file them twelve
    months late, so they are pushed back a year.
    """

    @pytest.mark.parametrize("statement_month", [1, 2])
    def test_late_month_transaction_belongs_to_the_previous_year(self, statement_month):
        transformer = _transformer(datetime(2024, statement_month, 10))
        assert transformer.to_iso8601("28 Dec") == "2023-12-28"

    @pytest.mark.parametrize("statement_month", [1, 2])
    def test_same_month_transaction_keeps_the_statement_year(self, statement_month):
        transformer = _transformer(datetime(2024, statement_month, 10))
        assert transformer.to_iso8601("05 Jan") == "2024-01-05"

    def test_march_statement_is_never_treated_as_cross_year(self):
        """The rollover only applies to statements issued in January or February."""
        transformer = _transformer(datetime(2024, 3, 10))
        assert transformer.to_iso8601("28 Dec") == "2024-12-28"

    def test_a_date_carrying_its_own_year_is_not_rolled_back(self):
        """No year was injected, so there is nothing to correct."""
        transformer = _transformer(datetime(2024, 1, 10), date_format="%d %b %Y")
        assert transformer.to_iso8601("28 Dec 2024") == "2024-12-28"


class TestFallback:
    def test_dateparser_handles_a_format_strptime_cannot(self):
        """`%d %b` cannot read a full month name with a year; dateparser can."""
        transformer = _transformer(datetime(2023, 7, 15), date_format="%d %b")
        assert transformer.to_iso8601("4 August 2023") == "2023-08-04"

    def test_ambiguous_numeric_dates_follow_the_configured_order(self):
        """DMY vs MDY is a per-bank setting, and the fallback must honour it."""
        assert _transformer(datetime(2023, 7, 15), order="DMY").to_iso8601("2023-08-04") == "2023-04-08"
        assert _transformer(datetime(2023, 7, 15), order="MDY").to_iso8601("2023-08-04") == "2023-08-04"

    def test_an_unparseable_date_raises(self):
        transformer = _transformer(datetime(2023, 7, 15))
        with pytest.raises(RuntimeError, match="Could not convert date"):
            transformer.to_iso8601("not a date at all")
