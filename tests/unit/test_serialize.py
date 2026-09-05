import json
import re
from datetime import datetime

from monopoly.constants import TransactionKind
from monopoly.serialize import SCHEMA_VERSION, assign_ids, statement_to_dict
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
    "direction",
}

BALANCE_KEYS = {"type", "amount", "date", "direction", "currency"}


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

    # no balance rows -> empty balances list, not absent
    assert envelope["balances"] == []

    # round-trips with the stdlib encoder: no datetime/date objects leak through
    assert json.loads(json.dumps(envelope)) == envelope


def test_period_start_surfaced_when_present(credit_statement):
    credit_statement.statement_date = datetime(2023, 6, 30)
    # cached_property is pre-seeded via the instance __dict__, like statement_date above
    credit_statement.period_start = datetime(2023, 6, 1)
    envelope = statement_to_dict(credit_statement, [_tx()])

    assert envelope["period_start"] == "2023-06-01"
    assert envelope["period_end"] == "2023-06-30"


def test_account_surfaced_per_transaction(credit_statement):
    credit_statement.statement_date = datetime(2023, 6, 30)
    tx = Transaction(transaction_date="2023-06-01", description="COFFEE", amount="4.50", currency="SGD", account="2031")
    envelope = statement_to_dict(credit_statement, [tx])

    assert envelope["transactions"][0]["account"] == "2031"


def test_schema_version_is_2():
    # v2 introduced the top-level `balances` split; guard against silent regression
    assert SCHEMA_VERSION == 2


def test_previous_balance_routed_to_balances(credit_statement):
    credit_statement.statement_date = datetime(2023, 6, 30)
    transactions = [
        Transaction(
            transaction_date="2023-06-01",
            description="PREVIOUS BALANCE",
            amount="100.00",
            direction="DR",
            currency="SGD",
            kind=TransactionKind.PREVIOUS_BALANCE,
        ),
        _tx(),
    ]
    envelope = statement_to_dict(credit_statement, transactions)

    # the carry-forward row is hoisted out of transactions
    assert len(envelope["transactions"]) == 1
    assert envelope["transactions"][0]["description"] == "COFFEE"

    # and lands in balances with the CAMT.053-aligned `previous` type
    assert len(envelope["balances"]) == 1
    balance = envelope["balances"][0]
    assert set(balance) == BALANCE_KEYS
    assert balance["type"] == "previous"
    assert balance["amount"] == -100.0
    assert balance["date"] == "2023-06-01"
    assert balance["direction"] == "debit"
    assert balance["currency"] == "SGD"

    # still JSON-native
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


def test_direction_normalized_to_credit_debit(credit_statement):
    credit_statement.statement_date = datetime(2023, 6, 30)
    transactions = [
        Transaction(transaction_date="2023-06-01", description="REFUND", amount="10.00", direction="CR"),
        Transaction(transaction_date="2023-06-02", description="COFFEE", amount="4.50"),
    ]
    envelope = statement_to_dict(credit_statement, transactions)
    directions = [tx["direction"] for tx in envelope["transactions"]]
    # explicit CR -> credit; a plain purchase (auto-negated amount) -> debit
    assert directions == ["credit", "debit"]
    # closed value set, never null
    assert all(d in ("credit", "debit") for d in directions)


def test_balance_null_when_absent_float_when_present(credit_statement):
    credit_statement.statement_date = datetime(2023, 6, 30)
    transactions = [
        Transaction(transaction_date="2023-06-01", description="A", amount="1.00"),
        Transaction(transaction_date="2023-06-02", description="B", amount="2.00", balance="100.00"),
    ]
    envelope = statement_to_dict(credit_statement, transactions)
    assert envelope["transactions"][0]["balance"] is None
    assert envelope["transactions"][1]["balance"] == 100.0


def _dup(**overrides):
    """A transaction whose identity fields collide by default (a real duplicate)."""
    base = {"transaction_date": "2023-06-01", "description": "SHOPEE", "amount": "100.00", "currency": "SGD"}
    base.update(overrides)
    return Transaction(**base)


def test_assign_ids_disambiguates_two_identical_rows():
    txs = [_dup(), _dup()]
    # sanity: the two rows genuinely collide at the content-hash level
    assert txs[0].content_hash == txs[1].content_hash
    ids = assign_ids(txs)
    assert len(set(ids)) == 2
    # first occurrence keeps the bare content hash (byte stability)
    assert ids[0] == txs[0].content_hash
    assert ids[1] != txs[1].content_hash


def test_assign_ids_disambiguates_three_identical_rows():
    txs = [_dup(), _dup(), _dup()]
    ids = assign_ids(txs)
    # guards off-by-one / non-monotonic ordinal
    assert len(set(ids)) == 3
    assert ids[0] == txs[0].content_hash


def test_assign_ids_leaves_unique_rows_as_content_hash():
    a = _dup(description="A")
    b = _dup(description="B")
    assert assign_ids([a, b]) == [a.content_hash, b.content_hash]


def test_assign_ids_is_deterministic():
    txs = [_dup(), _dup(), _dup(description="OTHER")]
    assert assign_ids(txs) == assign_ids(txs)


def test_envelope_gives_duplicate_rows_distinct_ids(credit_statement):
    credit_statement.statement_date = datetime(2023, 6, 30)
    envelope = statement_to_dict(credit_statement, [_dup(), _dup()])
    ids = [tx["id"] for tx in envelope["transactions"]]
    assert len(set(ids)) == 2


def test_credit_prev_balance_prepend_preserves_duplicate_ordinals(credit_statement, monkeypatch):
    """`post_process_transactions` prepends a synthetic prev-balance row via
    insert(0, ...). Ensure the reorder doesn't break ordinal assignment for a
    real duplicate pair, and the synthetic row isn't content-identical to them."""
    match = re.compile(r"(?P<description>PREV BAL) (?P<amount>[\d.]+)").search("PREV BAL 500.00")
    monkeypatch.setattr(credit_statement, "get_prev_month_balances", lambda: [match])

    processed = credit_statement.post_process_transactions([_dup(), _dup()])

    # synthetic row prepended
    assert len(processed) == 3
    # not content-identical to the real duplicates (would otherwise steal an ordinal)
    assert processed[0].content_hash != processed[1].content_hash

    ids = assign_ids(processed)
    assert len(set(ids)) == 3
    # the real duplicate pair (now at indices 1, 2) is still disambiguated
    assert ids[1] != ids[2]
