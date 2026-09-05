import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PaymentSummaryConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import TextIdentifier


class Trust(BankBase):
    name = "trust"

    credit = StatementConfig(
        currency="SGD",
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(
            r"-\s*"
            r"(?P<day>\d{2})\s+"
            r"(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
            r".*?"
            r"(?P<year>20\d{2}\b)"
        ),
        header_pattern=re.compile(
            r"(Posting date.*Description.*Amount in SGD"
            r"|Transaction\s+Posting.*Amount in\s+Amount in)"
        ),
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            rf"(?:{ISO8601.DD_MMM}\s+)?"  # Optional posting date
            r"(?P<description>(?:(?!Total outstanding balance).)*?)"
            r"(?P<direction>\+)?"
            f"{SharedPatterns.AMOUNT}"
            r"$"  # necessary to ignore FCY
        ),
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            include_prev_margin=99,
            multiline_statement_date=True,
        ),
        safety_check=True,
        transaction_date_format="%d %b",
        payment_summary_config=PaymentSummaryConfig(
            # summary block: "Statement balance S$681.27 / Minimum amount due S$50.00 / Payment due date 2 Sep 2024"
            payment_due_date=re.compile(r"Payment due date\s+(?P<due_date>\d{1,2}\s+\w{3}\s+\d{4})"),
            total_amount_due=re.compile(r"Statement balance\s+S\$\s*(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"),
            minimum_payment=re.compile(r"Minimum amount due\s+S\$\s*(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"),
        ),
    )

    identifiers = [[TextIdentifier("Trust Bank Singapore Limited")]]

    statement_configs = [credit]
