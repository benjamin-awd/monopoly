import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PdfConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Hsbc(BankBase):
    name = "hsbc"

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"From \d{{2}} \w{{3}} \d{{4}} to {ISO8601.DD_MMM_YYYY}"),
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        prev_balance_pattern=re.compile(
            r"(?P<description>Previous Statement Balance?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=re.compile(
            rf"(?P<posting_date>{ISO8601.DD_MMM_RELAXED})\s+"
            rf"(?P<transaction_date>{ISO8601.DD_MMM_RELAXED})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED
        ),
        transaction_date_format="%d %b",
        multiline_config=MultilineConfig(multiline_descriptions=True),
    )

    email_statement_identifier = [
        MetadataIdentifier(
            title="PRJ_BEAGLE_ST_CNS_SGH_APP_Orchid",
            author="Registered to:",
            creator="OpenText Exstream",
        ),
        TextIdentifier("HSBC"),
    ]

    web_and_mobile_statement_identifier = [
        MetadataIdentifier(format="PDF 1.7", producer="OpenText Output Transformation Engine - 20.4"),
    ]

    pdf_config = PdfConfig(
        page_bbox=(0, 0, 379, 840),
        ocr_identifiers=[web_and_mobile_statement_identifier],
    )

    identifiers = [email_statement_identifier, web_and_mobile_statement_identifier]

    statement_configs = [credit]
