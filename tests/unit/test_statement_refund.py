from monopoly.constants import CreditTransactionPatterns
from monopoly.pdf import PdfPage
from monopoly.statements import BaseStatement, Transaction


def test_statement_process_refund(statement: BaseStatement):
    page_content = (
        "08 SEP  AIRBNB * FOO123  456 GB  (343.01)\n"
        "14 AUG  AIRBNB * FOO123  456 GB  343.01\n"
        ""
    )
    page = PdfPage(raw_text=page_content)
    statement.statement_config.transaction_pattern = CreditTransactionPatterns.CITIBANK
    statement.pages = [page]
    expected_transactions = [
        Transaction(
            transaction_date="08 SEP",
            description="AIRBNB * FOO123 456 GB",
            amount=343.01,
            suffix="CR",
        ),
        Transaction(
            transaction_date="14 AUG",
            description="AIRBNB * FOO123 456 GB",
            amount=-343.01,
            suffix=None,
        ),
    ]
    assert statement.transactions == expected_transactions
