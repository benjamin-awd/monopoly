import re
from datetime import datetime

from pandas import DataFrame

from monopoly.constants import DATE
from monopoly.pdf import PDF


class OCBC(PDF):
    def __init__(self, file_path: str, password: str = ""):
        super().__init__(file_path)

        self.password: str = password
        self.regex_pattern: str = r"(\d+\/\d+)\s*(.*?)\s*([\d.,]+)$"
        self.statement_date_pattern: str = r"\d{2}\-\d{2}\-\d{4}"
        self.statement_date: datetime
        self.bank = "OCBC"
        self.account_name = "365"

    def extract(self) -> DataFrame:
        df = super().extract()
        self.statement_date = self._extract_statement_date()
        return df

    def _extract_statement_date(self) -> datetime:
        first_page = self.pages[0]
        for line in first_page:
            if match := re.match(self.statement_date_pattern, line):
                statement_date = match.group()
                return datetime.strptime(statement_date, "%d-%m-%Y")

    def transform(self) -> DataFrame:
        df = super().transform()
        df = self._transform_dates(self.df, self.statement_date)
        return df

    @staticmethod
    def _transform_dates(df: DataFrame, statement_date: datetime):
        def convert_date(row, statement_date: datetime):
            statement_year = statement_date.year
            statement_month = statement_date.month
            day, month = [int(i) for i in row[DATE].split("/")]

            # Deal with mixed years from Jan/Dec
            if statement_month == 1:
                if month == 1:
                    year = statement_year

                if month == 12:
                    year = statement_year - 1

            else:
                year = statement_year

            return f"{year}-{month:02d}-{day:02d}"

        df[DATE] = df.apply(
            lambda row: convert_date(row, statement_date), axis=1
        )

        return df
