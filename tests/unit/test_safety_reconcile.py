import re

import pytest

from monopoly.config import StatementConfig
from monopoly.constants import EntryType
from monopoly.pdf import PdfPage
from monopoly.statements import BaseStatement, CreditStatement, Transaction
from monopoly.statements.base import SafetyCheckError
from monopoly.statements.safety import sums_reconcile


def _tx(amount: float) -> Transaction:
    return Transaction(transaction_date="01/01", description="x", amount=amount, auto_direction=False)


class TestSumsReconcile:
    def test_both_totals_present_reconciles(self):
        transactions = [_tx(10.0), _tx(20.0), _tx(-5.0)]
        assert sums_reconcile(transactions, {30.0, 5.0}) is True

    def test_missing_credit_total_does_not_reconcile(self):
        assert sums_reconcile([_tx(10.0), _tx(-5.0)], {10.0}) is False

    def test_missing_debit_total_does_not_reconcile(self):
        assert sums_reconcile([_tx(10.0), _tx(-5.0)], {5.0}) is False

    def test_one_sided_statement_needs_zero_present(self):
        """An all-debit statement has a credit total of 0, which must be in the set."""
        assert sums_reconcile([_tx(10.0)], {10.0}) is False
        assert sums_reconcile([_tx(10.0)], {10.0, 0.0}) is True

    def test_totals_are_rounded_to_two_places(self):
        assert sums_reconcile([_tx(0.1), _tx(0.2)], {0.3, 0.0}) is True


class TestBaseStatementIsAbstract:
    def test_cannot_be_instantiated(self):
        """
        The safety check is now enforced at construction, not at call time.

        It was previously a `raise NotImplementedError` body, which only fired
        once a statement had already been parsed.
        """
        config = StatementConfig(
            statement_type=EntryType.CREDIT,
            transaction_pattern=re.compile("foo"),
            statement_date_pattern=re.compile("bar"),
            header_pattern=re.compile("baz"),
        )
        with pytest.raises(TypeError, match="abstract method 'perform_safety_check'"):
            BaseStatement(pages=[], bank_name="bank", config=config, header="")


class TestCreditFallbackMessage:
    def test_credit_specific_message_now_surfaces(self):
        """
        The credit message used to be unreachable.

        `CreditStatement` called `DebitStatement.perform_safety_check(self)`,
        which *raises* rather than returning False — so its generic message
        pre-empted the more informative credit one. Now that the fallback is a
        pure predicate, the credit branch reports its own failure.
        """
        config = StatementConfig(
            statement_type=EntryType.CREDIT,
            transaction_pattern=re.compile("foo"),
            statement_date_pattern=re.compile("bar"),
            header_pattern=re.compile("baz"),
        )
        statement = CreditStatement([PdfPage("Statement Page 1\nno totals listed here\n")], "bank", config, "header")
        statement.transactions = [_tx(10.0), _tx(20.0)]

        with pytest.raises(SafetyCheckError, match="Total amount 30.0 cannot be found in credit statement"):
            statement.perform_safety_check()
