from monopoly.handler import StatementHandler


# pylint: disable=duplicate-code
def example():
    """Example showing how monopoly can be used to extract data from
    a single bank statement
    """
    handler = StatementHandler(file_path="src/monopoly/examples/example_statement.pdf")

    # This runs pdftotext on the PDF and
    # extracts transactions as raw text
    statement = handler.extract()

    # Dates are converted into an ISO 8601 date format
    transformed_df = handler.transform(
        df=statement.df,
        statement_date=statement.statement_date,
        transaction_date_order=statement.config.transaction_date_order,
    )

    # Parsed transactions writen to a CSV file in the "example" directory
    handler.load(
        df=transformed_df, statement=statement, output_directory="src/monopoly/examples"
    )


if __name__ == "__main__":
    example()
