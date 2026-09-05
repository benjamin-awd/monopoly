import re

import pytest

from monopoly.config import PaymentSummaryConfig, StatementConfig, compile_pattern
from monopoly.constants import EntryType
from monopoly.constants.date import ISO8601


def _config(**overrides) -> StatementConfig:
    defaults = {
        "statement_type": EntryType.CREDIT,
        "transaction_pattern": re.compile("foo"),
        "statement_date_pattern": re.compile("bar"),
        "header_pattern": re.compile("baz"),
    }
    return StatementConfig(**{**defaults, **overrides})


class TestCompilePattern:
    def test_string_is_compiled(self):
        assert compile_pattern(r"\d+") == re.compile(r"\d+")

    def test_regex_enum_yields_its_compiled_pattern(self):
        assert compile_pattern(ISO8601.DD_MMM_YYYY) is ISO8601.DD_MMM_YYYY.regex

    def test_compiled_pattern_passes_through_unchanged(self):
        pattern = re.compile("already compiled")
        assert compile_pattern(pattern) is pattern

    def test_none_stays_none(self):
        assert compile_pattern(None) is None

    @pytest.mark.parametrize("value", [123, 4.5, object(), ["a"]])
    def test_unsupported_type_raises_at_once(self, value):
        with pytest.raises(TypeError, match="Expected a compiled pattern"):
            compile_pattern(value)


class TestStatementConfigNormalisation:
    def test_every_spelling_lands_as_a_compiled_pattern(self):
        config = _config(
            transaction_pattern=r"(?P<description>.*)",
            statement_date_pattern=ISO8601.DD_MMM_YYYY,
            header_pattern=re.compile("HEADER"),
        )

        assert isinstance(config.transaction_pattern, re.Pattern)
        assert isinstance(config.statement_date_pattern, re.Pattern)
        assert isinstance(config.header_pattern, re.Pattern)

    def test_optional_patterns_normalise_or_stay_none(self):
        config = _config(prev_balance_pattern=r"PREVIOUS BALANCE")

        assert isinstance(config.prev_balance_pattern, re.Pattern)
        assert config.filename_fallback_pattern is None

    def test_bad_pattern_fails_at_construction_not_at_use(self):
        """
        Validation used to be deferred to `DateResolver.resolve()`.

        Failing in the constructor means a malformed bank config cannot be
        built at import time, rather than surfacing mid-parse.
        """
        with pytest.raises(TypeError, match="Expected a compiled pattern"):
            _config(statement_date_pattern=123)


class TestPaymentSummaryConfigNormalisation:
    def test_patterns_normalise(self):
        config = PaymentSummaryConfig(
            payment_due_date=r"DUE (?P<due_date>.*)",
            total_amount_due=re.compile(r"TOTAL (?P<amount>.*)"),
        )

        assert isinstance(config.payment_due_date, re.Pattern)
        assert isinstance(config.total_amount_due, re.Pattern)
        assert config.minimum_payment is None
