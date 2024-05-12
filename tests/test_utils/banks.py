from monopoly.generic import GenericStatementHandler
from monopoly.handler import StatementHandler


def generate_test_cases_with_handlers(test_cases_data, statement_type: str):
    test_cases = []
    if statement_type == "credit":
        for bank, amount, date in test_cases_data:
            test_cases.append((bank, amount, date, GenericStatementHandler))
            test_cases.append((bank, amount, date, StatementHandler))

    if statement_type == "debit":
        for bank, debit_amount, credit_amount, date in test_cases_data:
            test_cases.append(
                (bank, debit_amount, credit_amount, date, GenericStatementHandler)
            )
            test_cases.append(
                (bank, debit_amount, credit_amount, date, StatementHandler)
            )

    return test_cases
