import re

import pytest

from monopoly.banks.base import BankBase
from monopoly.config import StatementConfig
from monopoly.constants import EntryType
from monopoly.identifiers import MetadataIdentifier, TextIdentifier

_VALID_CONFIG = StatementConfig(
    statement_type=EntryType.DEBIT,
    transaction_pattern=re.compile(r"(?P<description>.+)\s+(?P<amount>[\d.]+)"),
    statement_date_pattern=re.compile(r"\d{4}-\d{2}-\d{2}"),
    header_pattern=re.compile(r"Date.*Description.*Amount"),
)


def _unique_name(suffix):
    return f"_test_bank_{suffix}"


class TestIdentifiersStructure:
    def test_flat_list_raises_type_error(self):
        with pytest.raises(TypeError, match="must be a list of lists"):

            class Bad(BankBase):
                name = _unique_name("flat")
                statement_configs = [_VALID_CONFIG]
                identifiers = [MetadataIdentifier(creator="x"), TextIdentifier("y")]

    def test_non_identifier_in_group_raises_type_error(self):
        with pytest.raises(TypeError, match="must be an instance of Identifier"):

            class Bad(BankBase):
                name = _unique_name("non_id")
                statement_configs = [_VALID_CONFIG]
                identifiers = [["not_an_identifier"]]


class TestNameValidation:
    def test_empty_name_raises_value_error(self):
        with pytest.raises(ValueError, match="must be a non-empty string"):

            class Bad(BankBase):
                name = ""
                statement_configs = [_VALID_CONFIG]
                identifiers = [[MetadataIdentifier(creator="x")]]

    def test_whitespace_name_raises_value_error(self):
        with pytest.raises(ValueError, match="must be a non-empty string"):

            class Bad(BankBase):
                name = "   "
                statement_configs = [_VALID_CONFIG]
                identifiers = [[MetadataIdentifier(creator="x")]]

    def test_duplicate_name_raises_value_error(self):
        class First(BankBase):
            name = _unique_name("dup")
            statement_configs = [_VALID_CONFIG]
            identifiers = [[MetadataIdentifier(creator="x")]]

        with pytest.raises(ValueError, match="duplicate bank name"):

            class Second(BankBase):
                name = _unique_name("dup")
                statement_configs = [_VALID_CONFIG]
                identifiers = [[MetadataIdentifier(creator="y")]]


class TestStatementConfigsValidation:
    def test_empty_list_raises_type_error(self):
        with pytest.raises(TypeError, match="must be a non-empty list"):

            class Bad(BankBase):
                name = _unique_name("empty_configs")
                statement_configs = []
                identifiers = [[MetadataIdentifier(creator="x")]]

    def test_none_raises_type_error(self):
        with pytest.raises(TypeError, match="must be a non-empty list"):

            class Bad(BankBase):
                name = _unique_name("none_configs")
                statement_configs = None
                identifiers = [[MetadataIdentifier(creator="x")]]

    def test_non_statement_config_raises_type_error(self):
        with pytest.raises(TypeError, match="must be an instance of StatementConfig"):

            class Bad(BankBase):
                name = _unique_name("bad_config")
                statement_configs = ["not_a_config"]
                identifiers = [[MetadataIdentifier(creator="x")]]


class TestTransactionPatternGroups:
    def test_missing_description_raises_value_error(self):
        bad_config = StatementConfig(
            statement_type=EntryType.DEBIT,
            transaction_pattern=re.compile(r"(?P<amount>[\d.]+)"),
            statement_date_pattern=re.compile(r"\d{4}-\d{2}-\d{2}"),
            header_pattern=re.compile(r"Header"),
        )
        with pytest.raises(ValueError, match="missing required named groups.*description"):

            class Bad(BankBase):
                name = _unique_name("no_desc")
                statement_configs = [bad_config]
                identifiers = [[MetadataIdentifier(creator="x")]]

    def test_missing_amount_raises_value_error(self):
        bad_config = StatementConfig(
            statement_type=EntryType.DEBIT,
            transaction_pattern=re.compile(r"(?P<description>.+)"),
            statement_date_pattern=re.compile(r"\d{4}-\d{2}-\d{2}"),
            header_pattern=re.compile(r"Header"),
        )
        with pytest.raises(ValueError, match="missing required named groups.*amount"):

            class Bad(BankBase):
                name = _unique_name("no_amt")
                statement_configs = [bad_config]
                identifiers = [[MetadataIdentifier(creator="x")]]


class TestEmptyIdentifiersSkipsValidation:
    def test_empty_identifiers_skips_checks(self):
        """GenericBank pattern: identifiers=[] should skip all structural checks."""

        class GenericLike(BankBase):
            name = _unique_name("generic_like")
            statement_configs = []
            identifiers = []

        assert GenericLike not in BankBase.registry


class TestValidBankPasses:
    def test_valid_bank_registered(self):
        class ValidBank(BankBase):
            name = _unique_name("valid")
            statement_configs = [_VALID_CONFIG]
            identifiers = [[MetadataIdentifier(creator="valid_creator")]]

        assert ValidBank in BankBase.registry
