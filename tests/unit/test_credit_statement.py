import re
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

from monopoly.statements import CreditStatement, Transaction


def test_prev_month_balance_found(credit_statement: CreditStatement):
    expected = "LAST MONTH'S BALANCE   84.89"

    pattern = re.compile(r"(?P<description>LAST MONTH'S BALANCE?)\s+(?P<amount>[\d.,]+)")
    credit_statement.config.prev_balance_pattern = pattern
    credit_statement.pages[0].lines = ["LAST MONTH'S BALANCE   84.89"]

    result = credit_statement.get_prev_month_balances()
    assert result[0].group() == expected


def test_multiple_prev_month_balance(credit_statement: CreditStatement):
    expected = [
        "LAST MONTH'S BALANCE   84.89",
        "LAST MONTH'S BALANCE  123.12",
    ]

    pattern = re.compile(r"(?P<description>LAST MONTH'S BALANCE?)\s+(?P<amount>[\d.,]+)")
    credit_statement.config.prev_balance_pattern = pattern
    credit_statement.pages[0].lines = [
        "LAST MONTH'S BALANCE   84.89",
        "foo",
        "LAST MONTH'S BALANCE  123.12",
    ]

    results = [match.group() for match in credit_statement.get_prev_month_balances()]
    assert results == expected


def test_prev_month_balance_not_found(credit_statement: CreditStatement):
    credit_statement.config.prev_balance_pattern = re.compile("foobar")
    credit_statement.pages[0].raw_text = "RawTextNotContainingPreviousMonthBalance"

    result = credit_statement.get_prev_month_balances()
    assert not result


def mock_get_prev_month_balances(transactions):
    @dataclass
    class MockRegexMatch:
        transaction_date: str
        description: str
        amount: int

        def groupdict(self):
            return {
                "transaction_date": self.transaction_date,
                "description": self.description,
                "amount": self.amount,
            }

    return [
        MockRegexMatch(transaction_date="1900-01-01", description="foo", amount=99.99),
        MockRegexMatch(transaction_date="1900-01-01", description="bar", amount=123.12),
    ]


@patch(
    "monopoly.statements.credit_statement.CreditStatement.get_prev_month_balances",
    mock_get_prev_month_balances,
)
def test_inject_prev_month_balance(credit_statement):
    transactions = [MagicMock(spec=Transaction) for _ in range(3)]
    for i in range(3):
        transactions[i].date = "2024-01-01"

    result = credit_statement.post_process_transactions(transactions)
    expected = [
        Transaction(
            transaction_date="2024-01-01",
            description="bar",
            amount=-123.12,
            polarity=None,
        ),
        Transaction(
            transaction_date="2024-01-01",
            description="foo",
            amount=-99.99,
            polarity=None,
        ),
    ]
    assert result[0] in expected
    assert result[1] in expected
    assert len(transactions) == 5
