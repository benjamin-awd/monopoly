from monopoly.examples import MonopolyBank


def example():
    """Example showing how monopoly can be used to extract data from
    a single bank statement
    """
    bank = MonopolyBank(
        file_path="monopoly/examples/example_statement.pdf",
    )

    # This runs Tesseract on the PDF and
    # extracts transactions as raw text
    pages = bank.get_pages()
    statement = bank.extract(pages)

    # Dates are converted into an ISO 8601 date format
    transformed_df = bank.transform(statement)
    print(transformed_df)

    # Files are saved to an output directory
    # monopoly/output/monopoly-credit-2023-08.csv
    bank.load(transformed_df, statement)


if __name__ == "__main__":
    example()
