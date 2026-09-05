import re
from unittest.mock import Mock

import pytest

from monopoly.config import StatementConfig
from monopoly.constants import EntryType
from monopoly.handler import STATEMENT_CLASSES, StatementHandler
from monopoly.pdf import PdfPage
from monopoly.statements import CreditStatement, DebitStatement, MissingHeaderError


def _config(statement_type: EntryType) -> StatementConfig:
    return StatementConfig(
        statement_type=statement_type,
        transaction_pattern=re.compile("foo"),
        statement_date_pattern=re.compile("bar"),
        header_pattern=re.compile("HEADER"),
    )


def _handler(*configs: StatementConfig, header_line: str = "HEADER") -> StatementHandler:
    parser = Mock()
    parser.pages = [PdfPage(f"{header_line}\n")]
    parser.file_path = None
    parser.bank.name = "testbank"
    parser.bank.statement_configs = list(configs)
    return StatementHandler(parser)


def test_every_entry_type_has_a_statement_class():
    """Guards the lookup table against a new EntryType being added silently."""
    assert set(STATEMENT_CLASSES) == set(EntryType)


@pytest.mark.parametrize(
    ("statement_type", "expected"),
    [(EntryType.DEBIT, DebitStatement), (EntryType.CREDIT, CreditStatement)],
)
def test_dispatch_builds_the_matching_statement_class(statement_type, expected):
    statement = _handler(_config(statement_type)).statement
    assert isinstance(statement, expected)


def test_first_config_with_a_matching_header_wins():
    debit, credit = _config(EntryType.DEBIT), _config(EntryType.CREDIT)
    assert isinstance(_handler(debit, credit).statement, DebitStatement)
    assert isinstance(_handler(credit, debit).statement, CreditStatement)


def test_no_matching_header_raises():
    with pytest.raises(MissingHeaderError, match="Could not find header in statement"):
        _ = _handler(_config(EntryType.DEBIT), header_line="nothing here").statement
