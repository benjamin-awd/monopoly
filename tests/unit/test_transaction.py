from monopoly.statements import Transaction


def test_transaction_handles_comma():
    transaction = Transaction(transaction_date="2099-09-10", description="foo", amount="123,123.12")
    assert transaction.amount == -123123.12


def test_transaction_handles_whitespace():
    transaction = Transaction(
        transaction_date="2099-09-10",
        description="   foo,     bar    ",
        amount="123,123.12",
    )
    assert transaction.description == "foo, bar"
