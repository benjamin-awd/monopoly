import re
from datetime import datetime

from pandas import DataFrame

from monopoly.constants import DATE
from monopoly.exceptions import UndefinedFilePathError
from monopoly.pdf import PDF


class OCBC(PDF):
    def __init__(self, file_path: str = "", password: str = ""):
        super().__init__(file_path)

        self.password: str = password
        self.regex_pattern: str = r"(\d+\/\d+)\s*(.*?)\s*([\d.,]+)$"
        self.statement_date_pattern: str = r"\d{2}\-\d{2}\-\d{4}"
        self.statement_date: datetime
        self.bank = "OCBC"
        self.account_name = "365"

    def extract(self) -> DataFrame:
        if not self.file_path:
            raise UndefinedFilePathError("File path must be defined")

        df = super().extract_df_from_pdf()
        self.statement_date = self._extract_statement_date()
        return df

    def _extract_statement_date(self) -> datetime:
        first_page = self.pages[0]
        for line in first_page:
            if match := re.match(self.statement_date_pattern, line):
                statement_date = match.group()
                return datetime.strptime(statement_date, "%d-%m-%Y")

    def transform(self, df: DataFrame) -> DataFrame:
        df = super().transform_amount_to_float(df)
        df = self._transform_dates(df, self.statement_date)
        return df

    @staticmethod
    def _transform_dates(df: DataFrame, statement_date: datetime) -> DataFrame:
        def convert_date(row):
            row_day, row_month = map(int, row[DATE].split("/"))

            # Deal with mixed years from Jan/Dec
            if statement_date.month == 1 and row_month == 12:
                row_year = statement_date.year - 1
            else:
                row_year = statement_date.year

            return f"{row_year}-{row_month:02d}-{row_day:02d}"

        df[DATE] = df.apply(convert_date, axis=1)
        return df
