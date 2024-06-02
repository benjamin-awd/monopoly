from datetime import datetime

from monopoly.config import DateOrder
from monopoly.pipeline import Pipeline
from monopoly.statements import Transaction


def test_transform_cross_year():
    raw_transactions = [
        Transaction(
            transaction_date="12/01", description="FAIRPRICE FINEST", amount="18.49"
        ),
        Transaction(
            transaction_date="28/12", description="DA PAOLO GASTRONOMIA", amount="19.69"
        ),
        Transaction(transaction_date="28/11", description="KOPITIAM", amount="5.00"),
    ]
    transformed_transactions = Pipeline.transform(
        transactions=raw_transactions,
        statement_date=datetime(2024, 1, 1),
        transaction_date_order=DateOrder("DMY"),
    )
    expected_transactions = [
        Transaction(
            transaction_date="2024-01-12", description="FAIRPRICE FINEST", amount=18.49
        ),
        Transaction(
            transaction_date="2023-12-28",
            description="DA PAOLO GASTRONOMIA",
            amount=19.69,
        ),
        Transaction(transaction_date="2023-11-28", description="KOPITIAM", amount=5.00),
    ]

    assert transformed_transactions == expected_transactions


def test_transform_within_year():
    raw_transactions = [
        Transaction(
            transaction_date="12/06", description="FAIRPRICE FINEST", amount="18.49"
        ),
        Transaction(
            transaction_date="12/06", description="DA PAOLO GASTRONOMIA", amount="19.69"
        ),
    ]

    transformed_transactions = Pipeline.transform(
        transactions=raw_transactions,
        statement_date=datetime(2023, 7, 1),
        transaction_date_order=DateOrder("DMY"),
    )

    expected_transactions = [
        Transaction(
            transaction_date="2023-06-12", description="FAIRPRICE FINEST", amount=18.49
        ),
        Transaction(
            transaction_date="2023-06-12",
            description="DA PAOLO GASTRONOMIA",
            amount=19.69,
        ),
    ]

    assert transformed_transactions == expected_transactions
