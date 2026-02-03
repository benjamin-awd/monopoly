"""Unit tests for NumberExtractor class."""

import pytest

from monopoly.pdf import PdfPage
from monopoly.statements.number_extractor import NumberExtractor


class TestNumberExtractorGetDecimalNumbers:
    """Tests for NumberExtractor._get_decimal_numbers() method."""

    def test_extracts_decimal_numbers(self):
        """Test basic decimal number extraction."""
        lines = [
            "These are some sample lines 123.45 and 67.89",
            "Another line with a decimal number 0.56 but not here 123",
            "No decimals in this line 45, maybe here 10.0 or not",
        ]
        extractor = NumberExtractor(pages=[])

        result = extractor._get_decimal_numbers(lines)

        assert result == {123.45, 67.89, 0.56, 10.0}

    def test_handles_comma_formatted_numbers(self):
        """Test extraction of comma-formatted numbers."""
        lines = ["Total amount: 1,234.56", "Another: 10,000.00"]
        extractor = NumberExtractor(pages=[])

        result = extractor._get_decimal_numbers(lines)

        assert 1234.56 in result
        assert 10000.00 in result

    def test_ignores_integers(self):
        """Test that plain integers without decimals are ignored."""
        lines = ["Integer only: 100", "Another integer: 50"]
        extractor = NumberExtractor(pages=[])

        result = extractor._get_decimal_numbers(lines)

        assert result == set()

    def test_handles_empty_lines(self):
        """Test handling of empty input."""
        extractor = NumberExtractor(pages=[])

        result = extractor._get_decimal_numbers([])

        assert result == set()

    def test_extracts_multiple_numbers_per_line(self):
        """Test extraction of multiple numbers on the same line."""
        lines = ["Transaction: 50.00 Balance: 1,500.75 Fee: 2.50"]
        extractor = NumberExtractor(pages=[])

        result = extractor._get_decimal_numbers(lines)

        assert result == {50.00, 1500.75, 2.50}


class TestNumberExtractorGetSubtotalSum:
    """Tests for NumberExtractor._get_subtotal_sum() method."""

    def test_sums_subtotals(self):
        """Test that subtotals are correctly summed."""
        pages = [
            PdfPage(raw_text="sub total 100.00\nother line\nsub total 50.25"),
        ]
        extractor = NumberExtractor(pages)

        result = extractor._get_subtotal_sum()

        assert result == 150.25

    def test_handles_case_insensitive_subtotal(self):
        """Test case-insensitive matching of 'sub total'."""
        pages = [
            PdfPage(raw_text="SUB TOTAL 100.00\nSub Total 50.00"),
        ]
        extractor = NumberExtractor(pages)

        result = extractor._get_subtotal_sum()

        assert result == 150.00

    def test_returns_zero_when_no_subtotals(self):
        """Test that zero is returned when no subtotals found."""
        pages = [PdfPage(raw_text="No subtotals here\nJust regular text")]
        extractor = NumberExtractor(pages)

        result = extractor._get_subtotal_sum()

        assert result == 0.0

    def test_handles_comma_formatted_subtotals(self):
        """Test handling of comma-formatted subtotal amounts."""
        pages = [PdfPage(raw_text="sub total 1,234.56")]
        extractor = NumberExtractor(pages)

        result = extractor._get_subtotal_sum()

        assert result == 1234.56

    def test_sums_across_multiple_pages(self):
        """Test that subtotals are summed across multiple pages."""
        pages = [
            PdfPage(raw_text="Page 1\nsub total 100.00"),
            PdfPage(raw_text="Page 2\nsub total 200.00"),
            PdfPage(raw_text="Page 3\nsub total 300.00"),
        ]
        extractor = NumberExtractor(pages)

        result = extractor._get_subtotal_sum()

        assert result == 600.00


class TestNumberExtractorGetAllNumbers:
    """Tests for NumberExtractor.get_all_numbers() method."""

    def test_combines_decimal_numbers_and_subtotal(self):
        """Test that all numbers include decimals from pages plus subtotal sum."""
        pages = [
            PdfPage(raw_text="Transaction 50.25\nsub total 100.00"),
            PdfPage(raw_text="Another 75.50"),
        ]
        extractor = NumberExtractor(pages)

        result = extractor.get_all_numbers()

        # Should include: 50.25, 100.00, 75.50, and subtotal sum 100.00
        assert 50.25 in result
        assert 100.00 in result
        assert 75.50 in result

    def test_handles_empty_pages(self):
        """Test handling when pages list is empty."""
        extractor = NumberExtractor(pages=[])

        result = extractor.get_all_numbers()

        # Should contain at least the subtotal sum (0.0)
        assert 0.0 in result

    def test_returns_set_type(self):
        """Test that result is a set (no duplicates)."""
        pages = [
            PdfPage(raw_text="Amount: 100.00\nSame amount: 100.00"),
        ]
        extractor = NumberExtractor(pages)

        result = extractor.get_all_numbers()

        assert isinstance(result, set)
        # 100.00 should only appear once
        assert list(result).count(100.00) == 1 or 100.00 in result


class TestNumberExtractorPatterns:
    """Tests for NumberExtractor regex pattern properties."""

    def test_number_pattern_matches_digits_and_separators(self):
        """Test that number pattern matches expected formats."""
        extractor = NumberExtractor(pages=[])
        pattern = extractor._number_pattern

        assert pattern.search("123.45")
        assert pattern.search("1,234.56")
        assert pattern.search("100")

    def test_decimal_pattern_requires_decimal_point(self):
        """Test that decimal pattern requires decimal point at end."""
        extractor = NumberExtractor(pages=[])
        pattern = extractor._decimal_pattern

        assert pattern.match("123.45")
        assert pattern.match("0.5")
        assert not pattern.match("123")
        assert not pattern.match("123.45.67")

    def test_subtotal_pattern_matches_subtotal_lines(self):
        """Test that subtotal pattern matches 'sub total' lines."""
        extractor = NumberExtractor(pages=[])
        pattern = extractor._subtotal_pattern

        assert pattern.search("sub total 100.00")
        assert pattern.search("SUB TOTAL 1,234.56")
        assert pattern.search("Sub Total amount 50.25")
        assert not pattern.search("total 100.00")  # 'sub' required
