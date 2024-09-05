from monopoly.banks import ExampleBank
from monopoly.pdf import PdfParser
from monopoly.pipeline import Pipeline


def example():
    """Example showing how monopoly can be used to extract data from
    a single bank statement

    You can pass in the bank class if you want to specify a specific bank,
    or use the BankDetector class to try to detect the bank automatically.
    """
    pipeline = Pipeline(
        file_path="src/monopoly/examples/example_statement.pdf", bank=ExampleBank
    )
    parser = PdfParser(pipeline.bank, pipeline.document)
    pages = parser.get_pages()

    # This runs pdftotext on the PDF and
    # extracts transactions as raw text
    statement = pipeline.extract(pages)

    # Dates are converted into an ISO 8601 date format
    transactions = pipeline.transform(statement)

    # Parsed transactions writen to a CSV file in the "example" directory
    file_path = pipeline.load(
        transactions=transactions,
        statement=statement,
        output_directory="src/monopoly/examples",
    )

    with open(file_path) as file:
        print(file.read()[0:248])


if __name__ == "__main__":
    example()
