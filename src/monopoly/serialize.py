"""
Build a versioned, JSON-serializable envelope from a parsed statement.

This is the richer output schema (see the JSON `--format`), distinct from the
4-column CSV. The builder emits only JSON-native types — no `datetime`/`date`
objects — so the returned dict can be handed straight to `json.dump` without a
custom encoder, and asserted directly in tests.
"""

from collections import Counter
from dataclasses import asdict
from datetime import date, datetime
from hashlib import sha256
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


def assign_ids(transactions: list[Transaction]) -> list[str]:
    """
    Return a unique per-row `id` for each transaction, in list order.

    This is the ONLY sanctioned source of the JSON `"id"`. The id is the
    transaction's `content_hash` for the first occurrence of a given fingerprint,
    and `sha256(repr((content_hash, n)))` for the nth (n>0) occurrence within this
    list. That disambiguates genuinely-distinct transactions sharing identical
    content (e.g. two identical same-day transfers) while leaving every
    non-duplicated id byte-identical to its bare `content_hash`.

    The ordinal is assigned in list order, so callers must pass transactions in a
    stable order (statement extraction order). The ordinal is stable within a
    statement but cannot guarantee cross-statement stability if a bank re-sorts
    identical same-day rows — inherent to a stateless parser (see docs).

    Do not use `Transaction.content_hash` directly as a per-row id; it collides
    for identical content. Always route through this function.
    """
    seen: Counter[str] = Counter()
    ids: list[str] = []
    for transaction in transactions:
        base = transaction.content_hash
        occurrence = seen[base]
        seen[base] += 1
        if occurrence == 0:
            ids.append(base)
        else:
            ids.append(sha256(repr((base, occurrence)).encode("utf-8")).hexdigest())
    return ids


def _transaction_to_dict(transaction: Transaction, tx_id: str) -> dict[str, Any]:
    return {
        "id": tx_id,
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
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "bank": statement.bank_name,
        "statement_type": str(statement.statement_type),
        "period_start": None,
        "period_end": _iso(statement.statement_date),
        "payment_summary": _payment_summary_to_dict(statement),
        "transactions": [
            _transaction_to_dict(tx, tx_id) for tx, tx_id in zip(transactions, assign_ids(transactions), strict=True)
        ],
    }
