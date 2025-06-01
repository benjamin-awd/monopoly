from monopoly.banks import ExampleBank
from monopoly.pdf import PdfDocument, PdfParser
from monopoly.pipeline import Pipeline


def example():
    """
    Extract data from example single bank statement.

    You can pass in the bank class if you want to specify a specific bank,
    or use the BankDetector class to try to detect the bank automatically.
    """
    document = PdfDocument(file_path="src/monopoly/examples/example_statement.pdf")
    parser = PdfParser(ExampleBank, document)
    pipeline = Pipeline(parser)

    # This runs pdftotext on the PDF and
    # extracts transactions as raw text
    statement = pipeline.extract()

    # Dates are converted into an ISO 8601 date format
    transactions = pipeline.transform(statement)

    # Parsed transactions writen to a CSV file in the "example" directory
    file_path = pipeline.load(
        transactions=transactions,
        statement=statement,
        output_directory="src/monopoly/examples",
    )

    with open(file_path, encoding="utf8"):
        pass


if __name__ == "__main__":
    example()
