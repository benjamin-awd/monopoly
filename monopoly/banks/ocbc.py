import re
from datetime import datetime

import pandas as pd
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
        df = self._transform_dates(self.df, self.statement_date)
        return df

    @staticmethod
    def _transform_dates(df: DataFrame, statement_date: datetime):
        def convert_date(row, statement_date: datetime):
            statement_year = statement_date.year
            statement_month = statement_date.month
            day, month = [int(i) for i in row[DATE].split("/")]

            # If my statement is in January, I have to convert dates
            if statement_month == 1:
                # Specifically, if the month is Jan, the year is 2024
                if month == 1:
                    year = statement_year

                # If the month is Dec, the year is 2023
                if month == 12:
                    year = statement_year - 1

            return pd.to_datetime(
                f"{year}-{month:02d}-{day:02d}", format="%Y-%m-%d"
            )

        df[DATE] = df.apply(
            lambda row: convert_date(row, statement_date), axis=1
        )

        return df
