"""Reconciliation shared by the debit and credit safety checks."""

from monopoly.statements.transaction import Transaction


def sums_reconcile(transactions: list[Transaction], numbers: set[float]) -> bool:
    """
    Report whether the debit and credit totals both appear in the document.

    Used where a statement prints its debits and credits as two separate
    figures rather than one net total. A pure predicate: callers decide what
    a failure means and which error to raise.
    """
    debit_total = round(abs(sum(t.amount for t in transactions if t.amount > 0)), 2)
    credit_total = round(abs(sum(t.amount for t in transactions if t.amount < 0)), 2)
    return debit_total in numbers and credit_total in numbers
