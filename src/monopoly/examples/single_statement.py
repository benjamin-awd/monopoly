from monopoly.examples import MonopolyBank


def example():
    """Example showing how monopoly can be used to extract data from
    a single bank statement
    """
    bank = MonopolyBank(
        file_path="tests/integration/banks/example/input.pdf",
    )

    # This runs pdftotext on the PDF and
    # extracts transactions as raw text
    statement = bank.extract()

    # Dates are converted into an ISO 8601 date format
    transformed_df = bank.transform(statement)
    print(transformed_df)

    # Parsed transactions writen to a CSV file in the "example" directory
    bank.load(transformed_df, statement, output_directory="src/monopoly/examples")


if __name__ == "__main__":
    example()
