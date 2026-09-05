import json

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


def test_transaction_stores_richer_fields():
    transaction = Transaction(
        transaction_date="2099-09-10",
        description="foo",
        amount="10.00",
        posting_date="2099-09-11",
        currency="SGD",
        account="1234",
    )
    assert transaction.posting_date == "2099-09-11"
    assert transaction.currency == "SGD"
    assert transaction.account == "1234"


def test_richer_fields_excluded_from_str_and_raw_dict():
    """The filename hash feeds off __str__, so new fields must not leak into it."""
    plain = Transaction(transaction_date="2099-09-10", description="foo", amount="10.00")
    enriched = Transaction(
        transaction_date="2099-09-10",
        description="foo",
        amount="10.00",
        posting_date="2099-09-11",
        currency="SGD",
        account="1234",
    )
    assert str(plain) == str(enriched)

    keys = set(enriched.as_raw_dict(show_polarity=True, show_balance=True))
    assert keys.isdisjoint({"posting_date", "currency", "account"})
    assert set(json.loads(str(enriched))) == {"date", "description", "amount"}


def _tx(**overrides):
    base = {"transaction_date": "2099-09-10", "description": "foo", "amount": "10.00"}
    base.update(overrides)
    return Transaction(**base)


def test_transaction_id_stable_across_identical_transactions():
    assert _tx().transaction_id == _tx().transaction_id
    # balance is excluded from identity: same id despite differing running balance
    assert _tx(balance="100.00").transaction_id == _tx(balance="999.00").transaction_id


def test_transaction_id_differs_on_amount_or_description():
    baseline = _tx().transaction_id
    assert _tx(amount="10.01").transaction_id != baseline
    assert _tx(description="bar").transaction_id != baseline
    assert _tx(currency="SGD").transaction_id != baseline


def test_transaction_id_not_in_str():
    tx = _tx(currency="SGD")
    assert tx.transaction_id not in str(tx)


def test_transaction_id_reflects_later_mutation():
    # not cached: reading the id early must not freeze a stale value
    tx = _tx()
    early = tx.transaction_id
    tx.currency = "SGD"
    assert tx.transaction_id != early


def test_balance_none_when_absent_float_when_present():
    assert _tx().balance is None
    assert _tx(balance="100.00").balance == 100.0
