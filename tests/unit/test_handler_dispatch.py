import re
from typing import ClassVar
from unittest.mock import Mock

import pytest

from monopoly.config import StatementConfig
from monopoly.constants import EntryType
from monopoly.banks import BankBase
from monopoly.handler import STATEMENT_CLASSES, select_statement
from monopoly.pdf import PdfPage
from monopoly.statements import BaseStatement, CreditStatement, DebitStatement, MissingHeaderError


def _config(statement_type: EntryType) -> StatementConfig:
    return StatementConfig(
        statement_type=statement_type,
        transaction_pattern=re.compile("foo"),
        statement_date_pattern=re.compile("bar"),
        header_pattern=re.compile("HEADER"),
    )


def _select(*configs: StatementConfig, header_line: str = "HEADER") -> BaseStatement:
    class _FakeBank(BankBase):
        name = "testbank"
        identifiers: ClassVar[list] = []
        statement_configs: ClassVar[list[StatementConfig]] = list(configs)

    parser = Mock()
    parser.pages = [PdfPage(f"{header_line}\n")]
    parser.file_path = None
    parser.bank = _FakeBank
    return select_statement(parser)


def test_every_entry_type_has_a_statement_class():
    """Guards the lookup table against a new EntryType being added silently."""
    assert set(STATEMENT_CLASSES) == set(EntryType)


@pytest.mark.parametrize(
    ("statement_type", "expected"),
    [(EntryType.DEBIT, DebitStatement), (EntryType.CREDIT, CreditStatement)],
)
def test_dispatch_builds_the_matching_statement_class(statement_type, expected):
    statement = _select(_config(statement_type))
    assert isinstance(statement, expected)


def test_first_config_with_a_matching_header_wins():
    debit, credit = _config(EntryType.DEBIT), _config(EntryType.CREDIT)
    assert isinstance(_select(debit, credit), DebitStatement)
    assert isinstance(_select(credit, debit), CreditStatement)


def test_no_matching_header_raises():
    with pytest.raises(MissingHeaderError, match="Could not find header in statement"):
        _select(_config(EntryType.DEBIT), header_line="nothing here")
