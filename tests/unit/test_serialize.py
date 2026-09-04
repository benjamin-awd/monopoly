import json
from datetime import datetime

from monopoly.serialize import SCHEMA_VERSION, statement_to_dict
from monopoly.statements import Transaction

TRANSACTION_KEYS = {
    "id",
    "transaction_date",
    "posting_date",
    "description",
    "amount",
    "currency",
    "account",
    "balance",
    "polarity",
}


def _tx():
    return Transaction(transaction_date="2023-06-01", description="COFFEE", amount="4.50", currency="SGD")


def test_envelope_shape_and_json_roundtrip(credit_statement):
    credit_statement.statement_date = datetime(2023, 6, 30)
    envelope = statement_to_dict(credit_statement, [_tx()])

    assert envelope["schema_version"] == SCHEMA_VERSION
    assert envelope["bank"] == "example"
    assert envelope["statement_type"] == "credit"
    assert envelope["period_start"] is None
    assert envelope["period_end"] == "2023-06-30"

    assert len(envelope["transactions"]) == 1
    tx = envelope["transactions"][0]
    assert set(tx) == TRANSACTION_KEYS
    assert tx["id"]  # non-empty stable hash
    assert tx["currency"] == "SGD"

    # round-trips with the stdlib encoder: no datetime/date objects leak through
    assert json.loads(json.dumps(envelope)) == envelope


def test_payment_summary_present_for_credit(credit_statement):
    credit_statement.statement_date = datetime(2023, 6, 30)
    envelope = statement_to_dict(credit_statement, [])
    assert isinstance(envelope["payment_summary"], dict)
    assert set(envelope["payment_summary"]) == {"payment_due_date", "total_amount_due", "minimum_payment"}


def test_payment_summary_none_for_non_credit(debit_statement):
    debit_statement.statement_date = datetime(2023, 6, 30)
    envelope = statement_to_dict(debit_statement, [])
    assert envelope["statement_type"] == "debit"
    assert envelope["payment_summary"] is None
