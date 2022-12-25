import re
from datetime import datetime


def get_payment_due_date(text: str):
    """Helper function to deal with bills split across a different year 
    (e.g. Dec 2021 and Jan 2022), and to transform dates into a YYYY-MM-DD format"""
    pattern = r"Statement Date (?P<month>\w+) (?P<day>\d+), (?P<year>\d+)"
    match = re.search(pattern, text)
    groups = match.groupdict()

    # Serialize the string and return a datetime object
    payment_due_date = " ".join(groups.values()) 
    date = datetime.strptime(payment_due_date, "%B %d %Y").date()
    return date
