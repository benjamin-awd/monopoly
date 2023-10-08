from monopoly.statement import Transaction


def test_transaction_handles_comma():
    transaction = Transaction("2099-09-10", "foo", "123,123.12")
    assert transaction.amount == 123123.12
