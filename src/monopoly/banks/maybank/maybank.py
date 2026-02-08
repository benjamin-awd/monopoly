import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PdfConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import Identifier, MetadataIdentifier, TextIdentifier


class Maybank(BankBase):
    name = "maybank"

    my_debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"(?:結單日期)[:\s]+{ISO8601.DD_MM_YY}"),
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT.*BALANCE)"),
        transaction_date_format="%d/%m/%y",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MM_YY})\s+"
            + SharedPatterns.DESCRIPTION
            # remove *\s
            + SharedPatterns.AMOUNT[:-3]
            + r"(?P<polarity>\-|\+)\s+"
            + SharedPatterns.BALANCE
        ),
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    my_credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MMM_YY,
        header_pattern=re.compile(r"(Date.*Description.*Amount)"),
        transaction_date_format="%d/%m",
        transaction_pattern=re.compile(
            rf"(?P<posting_date>{ISO8601.DD_MM})\s+"
            rf"(?P<transaction_date>{ISO8601.DD_MM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
        ),
        prev_balance_pattern=re.compile(
            r"(?P<description>YOUR PREVIOUS STATEMENT BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    sg_credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(f"AS AT {ISO8601.DD_MMM_YYYY}"),
        header_pattern=re.compile(r"(.*DESCRIPTION OF TRANSACTION.*TRANSACTION AMOUNT)"),
        transaction_pattern=re.compile(
            r"(?P<posting_date>\b[A-Z]?\d{1,2}(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b)\s+"
            r"(?P<transaction_date>\b[A-Z]?\d{1,2}(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b)\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED
        ),
        prev_balance_pattern=re.compile(
            r"(?P<description>OUTSTANDING\s+BALANCE\s+BROUGHT\s+FORWARD?)\s+"
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
    )

    sg_credit_identifier: list[list[Identifier]] = [[TextIdentifier("maybank2u.com.sg"), TextIdentifier("PAYMENT DUE")]]

    identifiers = [
        *sg_credit_identifier,
        [
            MetadataIdentifier(
                author="Maybank2U.com",
                creator="Maybank2u.com",
                producer="iText",
            ),
        ],
        [
            MetadataIdentifier(
                title="Credit Card Statement",
                author="Maybank2U.com",
                producer="iText",
            ),
        ],
    ]

    pdf_config = PdfConfig(
        ocr_identifiers=sg_credit_identifier,
    )

    statement_configs = [my_credit, my_debit, sg_credit]
