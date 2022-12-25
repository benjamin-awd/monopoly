import re
import pandas as pd
from datetime import datetime


from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams


class PDF:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.raw_text: str = None
        self.df: pd.DataFrame = None
        self.payment_due_date: datetime = None

    def extract(self):
        # Parse raw text with pdfminer, and set char margin to 100 so that log lines are parsed
        self.raw_text = extract_text(self.file_path, laparams=LAParams(char_margin=100))
        
        # Define the regular expression pattern to match the data
        pattern = r"(\d{2} \w{3}) (.*) (.*) (.*) (\d+\.\d+)"

        # Split the data into lines
        lines = self.raw_text.split("\n")

        extracted_data = []
        df = pd.DataFrame(columns=["Date", "Vendor", "Location", "Country Code", "Amount"])

        for line in lines:
            match = re.match(pattern, line)
            if match:
                date = match.group(1)
                vendor = match.group(2)
                location = match.group(3)
                country_code = match.group(4)
                amount = match.group(5)

                extracted_data.append(
                    {
                        "Date": date,
                        "Vendor": vendor,
                        "Location": location,
                        "Country Code": country_code,
                        "Amount": amount,
                    }
            )

        # Append the extracted data to the DataFrame as a new row
        self.df = pd.concat([df, pd.DataFrame(extracted_data)])

        self.payment_due_date = self._get_payment_due_date()

    def transform(self):
        self.df["Date"] = self.df["Date"].apply(self._transform_dates)
        self.df["Date"] = pd.to_datetime(self.df["Date"], format="%d %b %Y")
        self.df["Amount"] = self.df["Amount"].astype(float)
        self.df["Location"] = self.df["Location"].str.upper()
    
    def _transform_dates(self, date: str):
        """Helper function to append year to date"""
        # Check if already has date
        match = re.match(r".*([1-3][0-9]{3})", date)
        if match:
            raise Exception("Date has already been updated")
        if self.payment_due_date.month == 1:
            if "DEC" in date:
                return date + " " + str(self.payment_due_date.year - 1)
            return date + " " + str(self.payment_due_date.year)
        else:
            return date + " " + str(self.payment_due_date.year)

    def _get_payment_due_date(self):
        """Helper function to deal with bills split across a different year 
        (e.g. Dec 2021 and Jan 2022), and to transform dates into a YYYY-MM-DD format"""
        pattern = r"Statement Date (?P<month>\w+) (?P<day>\d+), (?P<year>\d+)"
        match = re.search(pattern, self.raw_text)
        groups = match.groupdict()

        # Serialize the string and return a datetime object
        payment_due_date = " ".join(groups.values()) 
        date = datetime.strptime(payment_due_date, "%B %d %Y").date()
        return date