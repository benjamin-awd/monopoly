from glob import glob

from monopoly.banks.ocbc import Ocbc


def ocbc_example():
    """Example showing how monopoly can be used to extract data from
    multiple bank statements in a directory
    """
    ocbc_statements = glob("statements/ocbc/*.pdf")
    for file_path in ocbc_statements:
        bank = Ocbc(
            file_path=file_path,
        )
        statement = bank.extract()
        transformed_df = bank.transform(statement)
        bank.load(transformed_df, statement)


if __name__ == "__main__":
    ocbc_example()
