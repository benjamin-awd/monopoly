from datetime import datetime
from re import compile as regex

from monopoly.config import MultilineConfig
from monopoly.statements import BaseStatement


def test_statement_date_multiline(statement: BaseStatement):
    statement.pages[0].lines = [
        "   01-01                                                      23 Apr 2025 - 23 May",
        "                                                                          Statement cycle",
        "   02-123                                                                            2025",
    ]

    statement.config.statement_date_pattern = regex(
        r"-\s*"
        r"(?P<day>\d{2})\s+"
        r"(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
        r".*?"
        r"(?P<year>20\d{2}\b)"
    )
    statement.config.multiline_config = MultilineConfig(multiline_statement_date=True)
    assert statement.statement_date == datetime(2025, 5, 23)
