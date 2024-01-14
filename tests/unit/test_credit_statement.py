from unittest.mock import MagicMock

from monopoly.statements import Transaction


def test_prev_month_balance_found(credit_statement):
    expected = [Transaction("1900-01-01", "LAST MONTH'S BALANCE", -84.89)]

    pattern = r"(?P<description>LAST MONTH'S BALANCE?)\s+(?P<amount>[\d.,]+)"
    credit_statement.config.prev_balance_pattern = pattern
    credit_statement.pages[0].raw_text = "LAST MONTH'S BALANCE   84.89"

    result = credit_statement.prev_month_balance
    assert result == expected


def test_multiple_prev_month_balance(credit_statement):
    expected = [
        Transaction("1900-01-01", "LAST MONTH'S BALANCE", -84.89),
        Transaction("1900-01-01", "LAST MONTH'S BALANCE", 123.12),
    ]

    pattern = r"(?P<description>LAST MONTH'S BALANCE?)\s+(?P<amount>[\d.,]+)"
    credit_statement.config.prev_balance_pattern = pattern
    credit_statement.pages[
        0
    ].raw_text = "LAST MONTH'S BALANCE   84.89\nfoo\nLAST MONTH'S BALANCE  123.12"

    result = credit_statement.prev_month_balance
    assert result == expected


def test_prev_month_balance_not_found(credit_statement):
    credit_statement.config.prev_balance_pattern = "foobar"
    credit_statement.pages[0].raw_text = "RawTextNotContainingPreviousMonthBalance"

    # Call the method and assert the result
    result = credit_statement.prev_month_balance
    assert not result


def test_inject_prev_month_balance(credit_statement):
    mock_prev_month_balance = [
        Transaction(transaction_date="1900-01-01", description="foo", amount=99.99),
        Transaction(transaction_date="1900-01-01", description="bar", amount=123.12),
    ]
    credit_statement.prev_month_balance = mock_prev_month_balance

    # Create a list of transactions (mocked for simplicity)
    transactions = [MagicMock(spec=Transaction) for _ in range(3)]
    for i in range(3):
        transactions[i].transaction_date = "2024-01-01"

    # Call the method and assert the result
    result = credit_statement._inject_prev_month_balance(transactions)
    assert result[0] in mock_prev_month_balance
    assert result[1] in mock_prev_month_balance
    assert len(transactions) == 5
