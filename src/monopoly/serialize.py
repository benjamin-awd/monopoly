"""
Build a versioned, JSON-serializable envelope from a parsed statement.

This is the richer output schema (see the JSON `--format`), distinct from the
4-column CSV. The builder emits only JSON-native types — no `datetime`/`date`
objects — so the returned dict can be handed straight to `json.dump` without a
custom encoder, and asserted directly in tests.
"""

from dataclasses import asdict
from datetime import date, datetime
from typing import Any

from monopoly.statements import BaseStatement, Transaction
from monopoly.statements.credit_statement import CreditStatement

# Single integer; bump ONLY on a breaking change (remove/rename a field, change a
# value's type/meaning/units, or restructure nesting). Adding a new optional/
# nullable field is NOT breaking and must NOT bump this — consumers are expected
# to ignore unrecognized fields.
# v2: balance rows moved out of `transactions` into the top-level `balances` list.
#     Breaking: not back/forward compatible with v1 for consumers that read
#     balance rows.
SCHEMA_VERSION = 2

# Turns the internal `kind` marker into the `type` value used in the JSON output.
_BALANCE_KIND_TO_TYPE = {"previous_balance": "previous"}


def _iso(value: date | datetime | None) -> str | None:
    """Coerce a date/datetime to an ISO date string, passing through None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        value = value.date()
    return value.isoformat()


def _payment_summary_to_dict(statement: BaseStatement) -> dict[str, Any] | None:
    """Serialize the payment summary for credit statements, else None."""
    if not isinstance(statement, CreditStatement):
        return None
    summary = asdict(statement.payment_summary)
    summary["payment_due_date"] = _iso(summary["payment_due_date"])
    return summary


def _balance_to_dict(transaction: Transaction) -> dict[str, Any]:
    """Serialize a balance carry-forward row (kind != "transaction")."""
    return {
        "type": _BALANCE_KIND_TO_TYPE.get(transaction.kind, transaction.kind),
        "amount": transaction.amount,
        "date": transaction.date,
        "direction": transaction.direction,
        "currency": transaction.currency,
    }


def _transaction_to_dict(transaction: Transaction) -> dict[str, Any]:
    return {
        "id": transaction.transaction_id,
        "transaction_date": transaction.date,
        "posting_date": transaction.posting_date,
        "description": transaction.description,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "account": transaction.account,
        "balance": transaction.balance,
        "direction": transaction.direction,
    }


def statement_to_dict(statement: BaseStatement, transactions: list[Transaction]) -> dict[str, Any]:
    """
    Build the versioned output envelope for a statement and its transactions.

    `period_end` is the statement date (period end); `period_start` is a nullable
    follow-up. `payment_summary` is populated for credit statements, else None.

    A previous-balance row is put in the top-level `balances` list instead of
    `transactions`, so `transactions` only holds real spending. The row still
    stays in the list internally; only the output separates them.
    """
    activity = [tx for tx in transactions if tx.kind == "transaction"]
    balances = [tx for tx in transactions if tx.kind != "transaction"]
    return {
        "schema_version": SCHEMA_VERSION,
        "bank": statement.bank_name,
        "statement_type": str(statement.statement_type),
        "period_start": None,
        "period_end": _iso(statement.statement_date),
        "payment_summary": _payment_summary_to_dict(statement),
        "balances": [_balance_to_dict(tx) for tx in balances],
        "transactions": [_transaction_to_dict(tx) for tx in activity],
    }
