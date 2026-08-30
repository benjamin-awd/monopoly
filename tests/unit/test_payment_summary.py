import re
from datetime import date
from unittest.mock import Mock

from monopoly.config import PaymentSummaryConfig, StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfPage
from monopoly.statements import PaymentSummary
from monopoly.statements.payment_summary import PaymentSummaryExtractor

DUE_DATE_PATTERN = re.compile(r"PAYMENT DUE DATE\s*:\s*(?P<due_date>\d{1,2}\s+\w{3}\s+\d{2,4})")
TOTAL_PATTERN = re.compile(r"TOTAL AMOUNT DUE\s+(?P<amount>[\d,]+\.\d{2})")
MINIMUM_PATTERN = re.compile(r"\d{2}-\d{2}-\d{4}\s+\d{2}-\d{2}-\d{4}.*S\$\s*(?P<amount>[\d,]+\.\d{2})")


def _config(payment_summary_config: PaymentSummaryConfig | None = None) -> StatementConfig:
    return StatementConfig(
        statement_type=EntryType.CREDIT,
        transaction_pattern="foo",
        statement_date_pattern="foo",
        header_pattern="foo",
        payment_summary_config=payment_summary_config,
    )


def _pages(lines: list[str]) -> list[PdfPage]:
    page = Mock(spec=PdfPage)
    page.lines = lines
    return [page]


def test_payment_summary_all_fields_extracted():
    config = _config(
        PaymentSummaryConfig(
            payment_due_date=DUE_DATE_PATTERN,
            total_amount_due=TOTAL_PATTERN,
            minimum_payment=MINIMUM_PATTERN,
        )
    )
    lines = [
        "    01-08-2023   24-08-2023   S$22,800   S$22,058.11   S$50.00",
        "                      TOTAL AMOUNT DUE   702.10",
        "                      PAYMENT DUE DATE : 24 AUG 23",
    ]

    result = PaymentSummaryExtractor(_pages(lines), config).extract()

    assert result == PaymentSummary(
        payment_due_date=date(2023, 8, 24),
        total_amount_due=702.10,
        minimum_payment=50.00,
    )


def test_payment_summary_strips_thousands_separator():
    config = _config(PaymentSummaryConfig(total_amount_due=TOTAL_PATTERN))

    result = PaymentSummaryExtractor(_pages(["TOTAL AMOUNT DUE   1,234.56"]), config).extract()

    assert result.total_amount_due == 1234.56


def test_payment_summary_returns_empty_without_config():
    result = PaymentSummaryExtractor(_pages(["TOTAL AMOUNT DUE   702.10"]), _config()).extract()

    assert result == PaymentSummary()


def test_payment_summary_is_partial_when_field_absent():
    config = _config(
        PaymentSummaryConfig(
            payment_due_date=DUE_DATE_PATTERN,
            total_amount_due=TOTAL_PATTERN,
            minimum_payment=MINIMUM_PATTERN,
        )
    )

    # only the total is present in the text
    result = PaymentSummaryExtractor(_pages(["TOTAL AMOUNT DUE   702.10"]), config).extract()

    assert result == PaymentSummary(total_amount_due=702.10)


def test_payment_summary_credit_balance_is_negative():
    # AMOUNT_EXTENDED_WITHOUT_EOL exposes the CR/parenthesis polarity that OCBC uses
    from monopoly.constants import SharedPatterns

    pattern = re.compile(r"TOTAL AMOUNT DUE\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL)
    config = _config(PaymentSummaryConfig(total_amount_due=pattern))

    cr_result = PaymentSummaryExtractor(_pages(["TOTAL AMOUNT DUE   412.16 CR"]), config).extract()
    paren_result = PaymentSummaryExtractor(_pages(["TOTAL AMOUNT DUE   (412.16)"]), config).extract()

    assert cr_result.total_amount_due == -412.16
    assert paren_result.total_amount_due == -412.16


def test_payment_summary_unparseable_date_is_none():
    config = _config(PaymentSummaryConfig(payment_due_date=re.compile(r"DUE:\s*(?P<due_date>.+)")))

    result = PaymentSummaryExtractor(_pages(["DUE: not-a-date"]), config).extract()

    assert result.payment_due_date is None
