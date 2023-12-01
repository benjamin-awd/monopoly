from monopoly.processors import ExampleBankProcessor


def example():
    """Example showing how monopoly can be used to extract data from
    a single bank statement
    """
    processor = ExampleBankProcessor(
        file_path="src/monopoly/examples/example_statement.pdf",
    )

    # This runs pdftotext on the PDF and
    # extracts transactions as raw text
    statement = processor.extract()

    # Dates are converted into an ISO 8601 date format
    transformed_df = processor.transform(statement)
    print(transformed_df)

    # Parsed transactions writen to a CSV file in the "example" directory
    processor.load(transformed_df, statement, output_directory="src/monopoly/examples")


if __name__ == "__main__":
    example()
