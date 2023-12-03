from monopoly.config import StatementConfig
from monopoly.constants import BankNames, MetadataIdentifier, SharedPatterns
from monopoly.processors.base import ProcessorBase


class ExampleBankProcessor(ProcessorBase):
    """Dummy class to help with reading the example PDF statement"""

    credit_config = StatementConfig(
        bank_name=BankNames.EXAMPLE,
        statement_date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        statement_date_format=r"%d-%m-%Y",
        prev_balance_pattern=(
            r"(?P<description>LAST MONTH'S BALANCE?)\s+" + SharedPatterns.AMOUNT
        ),
        transaction_pattern=(
            r"(?P<transaction_date>\d+/\d+)\s*"
            r"(?P<description>.*?)\s*" + SharedPatterns.AMOUNT
        ),
        transaction_date_format=r"%d/%m",
    )

    debit_config = None

    identifiers = [
        MetadataIdentifier(
            creator="Adobe Acrobat 23.3", producer="Adobe Acrobat Pro (64-bit)"
        )
    ]
