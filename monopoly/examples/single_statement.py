from monopoly.banks.ocbc import Ocbc


def ocbc_example():
    """Example showing how monopoly can be used to extract data from
    a single bank statement
    """
    bank = Ocbc(
        file_path="monopoly/examples/ocbc_365_example.pdf",
    )

    # This runs Tesseract on the PDF and
    # extracts transactions as raw text
    statement = bank.extract()

    # Dates are converted into an ISO 8601 date format
    transformed_df = bank.transform(statement)
    print(transformed_df)

    # Files are saved to an output directory
    # monopoly/output/OCBC-Credit-2023-08.csv
    bank.load(transformed_df, statement)


if __name__ == "__main__":
    ocbc_example()
