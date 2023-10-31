from monopoly.statement import Transaction


def test_transaction_handles_comma():
    transaction = Transaction("2099-09-10", "foo", "123,123.12")
    assert transaction.amount == 123123.12


def test_transaction_handles_whitespace():
    transaction = Transaction("2099-09-10", "   foo,     bar    ", "123,123.12")
    assert transaction.description == "foo, bar"
