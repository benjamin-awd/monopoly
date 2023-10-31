from dataclasses import fields

from monopoly.constants import StatementFields
from monopoly.statement import Transaction


def test_transaction_fields_match_statement_fields():
    """Transaction should be consistent with StatementField values"""

    transaction_field_names = {field.name for field in fields(Transaction)}
    statement_field_values = {field.value for field in StatementFields}

    # Check if the fields in Transaction match the enum values in StatementFields
    assert transaction_field_names == statement_field_values
