import re

from monopoly.config import StatementConfig
from monopoly.constants import Direction, EntryType, SharedPatterns, TransactionKind
from monopoly.pdf import PdfPage
from monopoly.statements import CreditStatement


def make_statement(page_text: str) -> CreditStatement:
    config = StatementConfig(
        statement_type=EntryType.CREDIT,
        header_pattern="foo",
        transaction_pattern=re.compile(r"(?P<transaction_date>\d+/\d+)\s+(?P<description>SHOP)\s+(?P<amount>[\d.]+)"),
        statement_date_pattern="",
        prev_balance_pattern=re.compile(
            r"(?P<description>PREVIOUS BALANCE)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
    )
    return CreditStatement(pages=[PdfPage(raw_text=page_text)], bank_name="example", config=config, header="foo")


def test_prev_balance_bare_minus_reads_as_credit():
    # on a credit statement a bare "-" marks a credit, for the balance row as for activity
    statement = make_statement("PREVIOUS BALANCE  100.00 -\n01/02  SHOP  5.00\n")
    prev, _ = statement.transactions

    assert prev.kind is TransactionKind.PREVIOUS_BALANCE
    assert prev.direction is Direction.CREDIT
    assert prev.amount == 100.0


def test_prev_balance_without_marker_is_debit():
    statement = make_statement("PREVIOUS BALANCE  100.00\n01/02  SHOP  5.00\n")
    prev, _ = statement.transactions

    assert prev.direction is Direction.DEBIT
    assert prev.amount == -100.0
    assert prev.date == "01/02"
