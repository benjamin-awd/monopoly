from datetime import datetime

from monopoly.config import DateOrder
from monopoly.pipeline import Pipeline
from monopoly.statements import BaseStatement, Transaction


def test_transform_yyyy_transaction(statement: BaseStatement):
    raw_transactions = [
        Transaction(
            transaction_date="01/12/2023",
            description="FAIRPRICE FINEST",
            amount="18.49",
        ),
    ]
    statement.transactions = raw_transactions
    statement.statement_date = datetime(2024, 1, 1)
    statement.config.transaction_date_order = DateOrder("DMY")
    transformed_transactions = Pipeline.transform(statement)
    expected_transactions = [
        Transaction(transaction_date="2023-12-01", description="FAIRPRICE FINEST", amount=18.49),
    ]

    assert transformed_transactions == expected_transactions


def test_transform_cross_year(statement: BaseStatement):
    raw_transactions = [
        Transaction(transaction_date="12/01", description="FAIRPRICE FINEST", amount="18.49"),
        Transaction(transaction_date="28/12", description="DA PAOLO GASTRONOMIA", amount="19.69"),
        Transaction(transaction_date="28/11", description="KOPITIAM", amount="5.00"),
    ]
    statement.transactions = raw_transactions
    statement.statement_date = datetime(2024, 1, 1)
    statement.config.transaction_date_order = DateOrder("DMY")
    transformed_transactions = Pipeline.transform(statement)
    expected_transactions = [
        Transaction(transaction_date="2024-01-12", description="FAIRPRICE FINEST", amount=18.49),
        Transaction(
            transaction_date="2023-12-28",
            description="DA PAOLO GASTRONOMIA",
            amount=19.69,
        ),
        Transaction(transaction_date="2023-11-28", description="KOPITIAM", amount=5.00),
    ]

    assert transformed_transactions == expected_transactions


def test_transform_normalizes_posting_date(statement: BaseStatement):
    statement.transactions = [
        Transaction(
            transaction_date="05/01",
            posting_date="07/01",
            description="FAIRPRICE FINEST",
            amount="18.49",
        ),
    ]
    statement.statement_date = datetime(2024, 1, 31)
    statement.config.transaction_date_order = DateOrder("DMY")
    statement.config.transaction_date_format = "%d/%m"

    [transaction] = Pipeline.transform(statement)

    # both dates are ISO 8601, not the raw captured strings
    assert transaction.date == "2024-01-05"
    assert transaction.posting_date == "2024-01-07"


def test_transform_within_year(statement: BaseStatement):
    raw_transactions = [
        Transaction(transaction_date="12/06", description="FAIRPRICE FINEST", amount="18.49"),
        Transaction(transaction_date="12/06", description="DA PAOLO GASTRONOMIA", amount="19.69"),
    ]

    statement.transactions = raw_transactions
    statement.statement_date = datetime(2023, 7, 1)
    statement.config.transaction_date_order = DateOrder("DMY")

    transformed_transactions = Pipeline.transform(statement)

    expected_transactions = [
        Transaction(transaction_date="2023-06-12", description="FAIRPRICE FINEST", amount=18.49),
        Transaction(
            transaction_date="2023-06-12",
            description="DA PAOLO GASTRONOMIA",
            amount=19.69,
        ),
    ]

    assert transformed_transactions == expected_transactions
