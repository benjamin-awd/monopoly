"""Unit tests for DateResolver class."""

import re
from datetime import datetime
from pathlib import Path

import pytest

from monopoly.config import DateOrder, MultilineConfig, StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfPage
from monopoly.statements.date_resolver import DateResolver


@pytest.fixture
def basic_config():
    """Basic config with a simple statement date pattern."""
    return StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"DATE.*AMOUNT"),
        transaction_pattern=re.compile(r"\d{2} \w{3}.*\d+\.\d+"),
        statement_date_pattern=re.compile(r"Statement Date[:\s]+(\d{1,2} \w{3} \d{4})"),
        statement_date_order=DateOrder("DMY"),
    )


@pytest.fixture
def named_groups_config():
    """Config with named capture groups for date parts."""
    return StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"DATE.*AMOUNT"),
        transaction_pattern=re.compile(r"\d{2} \w{3}.*\d+\.\d+"),
        statement_date_pattern=re.compile(r"Statement Date[:\s]+(?P<day>\d{1,2})\s+(?P<month>\w{3})\s+(?P<year>\d{4})"),
        statement_date_order=DateOrder("DMY"),
    )


@pytest.fixture
def multiline_config():
    """Config with multiline statement date enabled."""
    return StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"DATE.*AMOUNT"),
        transaction_pattern=re.compile(r"\d{2} \w{3}.*\d+\.\d+"),
        statement_date_pattern=re.compile(r"Statement Date[:\s]+(\d{1,2} \w{3} \d{4})"),
        statement_date_order=DateOrder("DMY"),
        multiline_config=MultilineConfig(multiline_statement_date=True),
    )


@pytest.fixture
def filename_fallback_config():
    """Config with filename fallback pattern."""
    return StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern=re.compile(r"DATE.*AMOUNT"),
        transaction_pattern=re.compile(r"\d{2} \w{3}.*\d+\.\d+"),
        statement_date_pattern=re.compile(r"Statement Date[:\s]+(\d{1,2} \w{3} \d{4})"),
        statement_date_order=DateOrder("DMY"),
        filename_fallback_pattern=re.compile(r"_([A-Za-z]{3})(\d{4})"),
    )


class TestDateResolverResolve:
    """Tests for DateResolver.resolve() method."""

    def test_extracts_date_from_content(self, basic_config):
        """Test that date is extracted from page content."""
        pages = [PdfPage(raw_text="Statement Date: 15 Nov 2023\nDATE AMOUNT\n01 Nov 100.00")]
        resolver = DateResolver(pages, basic_config)

        result = resolver.resolve()

        assert result.year == 2023
        assert result.month == 11
        assert result.day == 15

    def test_extracts_date_with_named_groups(self, named_groups_config):
        """Test that date is extracted using named capture groups."""
        pages = [PdfPage(raw_text="Statement Date: 20 Dec 2024\nDATE AMOUNT")]
        resolver = DateResolver(pages, named_groups_config)

        result = resolver.resolve()

        assert result.year == 2024
        assert result.month == 12
        assert result.day == 20

    def test_searches_multiple_pages(self, basic_config):
        """Test that resolver searches through multiple pages."""
        pages = [
            PdfPage(raw_text="Page 1 - no date here"),
            PdfPage(raw_text="Page 2 - Statement Date: 10 Jan 2025"),
        ]
        resolver = DateResolver(pages, basic_config)

        result = resolver.resolve()

        assert result.year == 2025
        assert result.month == 1
        assert result.day == 10

    def test_raises_when_date_not_found(self, basic_config):
        """Test that ValueError is raised when no date is found."""
        pages = [PdfPage(raw_text="No date information here")]
        resolver = DateResolver(pages, basic_config)

        with pytest.raises(ValueError, match="Statement date not found"):
            resolver.resolve()

    def test_raises_for_invalid_pattern_type(self, basic_config):
        """Test that TypeError is raised for invalid pattern type."""
        basic_config.statement_date_pattern = "not a pattern"
        pages = [PdfPage(raw_text="Statement Date: 15 Nov 2023")]
        resolver = DateResolver(pages, basic_config)

        with pytest.raises(TypeError, match="Pattern must be one of"):
            resolver.resolve()

    def test_filename_fallback_when_content_has_no_date(self, filename_fallback_config):
        """Test that filename fallback is used when content has no date."""
        pages = [PdfPage(raw_text="No date in content")]
        file_path = Path("/tmp/eStatement_Nov2025_timestamp.pdf")
        resolver = DateResolver(pages, filename_fallback_config, file_path)

        result = resolver.resolve()

        assert result.year == 2025
        assert result.month == 11
        assert result.day == 1

    def test_content_takes_precedence_over_filename(self, filename_fallback_config):
        """Test that content date takes precedence over filename."""
        pages = [PdfPage(raw_text="Statement Date: 15 Mar 2024")]
        file_path = Path("/tmp/eStatement_Nov2025_timestamp.pdf")
        resolver = DateResolver(pages, filename_fallback_config, file_path)

        result = resolver.resolve()

        # Should use content date, not filename
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 15


class TestDateResolverGetSearchText:
    """Tests for DateResolver._get_search_text() method."""

    def test_returns_single_line_without_multiline_config(self, basic_config):
        """Test that single line is returned when multiline is disabled."""
        pages = [PdfPage(raw_text="line1\nline2\nline3")]
        resolver = DateResolver(pages, basic_config)
        lines = ["line1", "line2", "line3"]

        result = resolver._get_search_text(lines, 0, "line1")

        assert result == "line1"

    def test_combines_lines_with_multiline_config(self, multiline_config):
        """Test that lines are combined when multiline is enabled."""
        pages = [PdfPage(raw_text="Statement\nDate:\n15 Nov 2023")]
        resolver = DateResolver(pages, multiline_config)
        lines = ["Statement", "Date:", "15 Nov 2023"]

        result = resolver._get_search_text(lines, 0, "Statement")

        assert "Statement" in result
        assert "Date:" in result
        assert "15 Nov 2023" in result


class TestDateResolverConstructDateString:
    """Tests for DateResolver._construct_date_string() static method."""

    def test_constructs_from_named_groups(self):
        """Test date construction from named groups."""
        pattern = re.compile(r"(?P<day>\d+)-(?P<month>\w+)-(?P<year>\d+)")
        match = pattern.search("15-Nov-2023")

        result = DateResolver._construct_date_string(match)

        assert result == "15-Nov-2023"

    def test_uses_group_1_without_named_groups(self):
        """Test date construction using group 1 when no named groups."""
        pattern = re.compile(r"Date: (\d+ \w+ \d+)")
        match = pattern.search("Date: 15 Nov 2023")

        result = DateResolver._construct_date_string(match)

        assert result == "15 Nov 2023"


class TestDateResolverExtractFromFilename:
    """Tests for DateResolver._extract_date_from_filename() method."""

    def test_extracts_date_from_filename(self, filename_fallback_config):
        """Test successful date extraction from filename."""
        pages = []
        file_path = Path("/tmp/eStatement_Dec2024_timestamp.pdf")
        resolver = DateResolver(pages, filename_fallback_config, file_path)

        result = resolver._extract_date_from_filename()

        assert result is not None
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 1

    def test_returns_none_without_file_path(self, filename_fallback_config):
        """Test that None is returned when no file path."""
        pages = []
        resolver = DateResolver(pages, filename_fallback_config, file_path=None)

        result = resolver._extract_date_from_filename()

        assert result is None

    def test_returns_none_without_fallback_pattern(self, basic_config):
        """Test that None is returned when no fallback pattern configured."""
        pages = []
        file_path = Path("/tmp/eStatement_Nov2025.pdf")
        resolver = DateResolver(pages, basic_config, file_path)

        result = resolver._extract_date_from_filename()

        assert result is None

    def test_returns_none_when_pattern_not_matched(self, filename_fallback_config):
        """Test that None is returned when filename doesn't match pattern."""
        pages = []
        file_path = Path("/tmp/random_filename.pdf")
        resolver = DateResolver(pages, filename_fallback_config, file_path)

        result = resolver._extract_date_from_filename()

        assert result is None
