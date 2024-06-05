from monopoly.pipeline import Pipeline


# pylint: disable=duplicate-code
def example():
    """Example showing how monopoly can be used to extract data from
    a single bank statement
    """
    pipeline = Pipeline(file_path="src/monopoly/examples/example_statement.pdf")

    # This runs pdftotext on the PDF and
    # extracts transactions as raw text
    statement = pipeline.extract()

    # Dates are converted into an ISO 8601 date format
    transactions = pipeline.transform(statement)

    # Parsed transactions writen to a CSV file in the "example" directory
    pipeline.load(
        transactions=transactions,
        statement=statement,
        output_directory="src/monopoly/examples",
    )


if __name__ == "__main__":
    example()
