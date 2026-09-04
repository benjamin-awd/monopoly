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

# Bump when the envelope shape changes in a way consumers must notice.
SCHEMA_VERSION = 1


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
        "polarity": transaction.polarity,
    }


def statement_to_dict(statement: BaseStatement, transactions: list[Transaction]) -> dict[str, Any]:
    """
    Build the versioned output envelope for a statement and its transactions.

    `period_end` is the statement date (period end); `period_start` is a nullable
    follow-up. `payment_summary` is populated for credit statements, else None.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "bank": statement.bank_name,
        "statement_type": str(statement.statement_type),
        "period_start": None,
        "period_end": _iso(statement.statement_date),
        "payment_summary": _payment_summary_to_dict(statement),
        "transactions": [_transaction_to_dict(tx) for tx in transactions],
    }
