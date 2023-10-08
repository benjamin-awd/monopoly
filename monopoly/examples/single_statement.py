from monopoly.bank import BankBase
from monopoly.helpers.constants import AccountType, BankNames
from monopoly.statement import StatementConfig


# fmt: off
class MonopolyBank(BankBase):
    """Dummy class to help with reading the example PDF statement"""
    statement_config = StatementConfig(
        bank_name=BankNames.EXAMPLE,
        account_type=AccountType.CREDIT,
        transaction_pattern=(
            r"(?P<date>\d+/\d+)\s*"
            r"(?P<description>.*?)\s*"
            r"(?P<amount>[\d.,]+)$"
        ),
        transaction_date_format=r"%d/%m",
        statement_date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        statement_date_format=r"%d-%m-%Y",
    )


def example():
    """Example showing how monopoly can be used to extract data from
    a single bank statement
    """
    bank = MonopolyBank(
        file_path="monopoly/examples/example_statement.pdf",
    )

    # This runs Tesseract on the PDF and
    # extracts transactions as raw text
    statement = bank.extract()

    # Dates are converted into an ISO 8601 date format
    transformed_df = bank.transform(statement)
    print(transformed_df)

    # Files are saved to an output directory
    # monopoly/output/monopoly-credit-2023-08.csv
    bank.load(transformed_df, statement)


if __name__ == "__main__":
    example()
