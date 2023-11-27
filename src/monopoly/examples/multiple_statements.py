from glob import glob

from monopoly.processors import Ocbc


def ocbc_example():
    """Example showing how monopoly can be used to extract data from
    multiple bank statements in a directory
    """
    ocbc_statements = glob("statements/ocbc/*.pdf")
    for file_path in ocbc_statements:
        processor = Ocbc(
            file_path=file_path,
        )
        statement = processor.extract()
        transformed_df = processor.transform(statement)
        processor.load(
            transformed_df, statement, output_directory="src/monopoly/examples"
        )


if __name__ == "__main__":
    ocbc_example()
