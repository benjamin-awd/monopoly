from re import compile as regex
from monopoly.constants import ISO8601
from monopoly.statements import BaseStatement
from monopoly.config import MultilineConfig
from datetime import datetime

def test_statement_date_multiline(statement: BaseStatement):
    statement.pages[0].lines = [
        "Statement cycle   23 Apr 2025 - 23 May",
        "                                2025"
    ]

    statement.config.statement_date_pattern = regex(rf"\- {ISO8601.DD_MMM_YYYY}")
    statement.config.multiline_config = MultilineConfig(multiline_statement_date=True, multiline_transactions=False)

    assert statement.statement_date == datetime(2025, 5, 23)
