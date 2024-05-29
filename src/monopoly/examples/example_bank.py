from monopoly.banks.base import BankBase
from monopoly.config import CreditStatementConfig
from monopoly.constants import InternalBankNames, MetadataIdentifier, SharedPatterns


class ExampleBank(BankBase):
    """Dummy class to help with reading the example PDF statement"""

    credit_config = CreditStatementConfig(
        bank_name=InternalBankNames.EXAMPLE,
        statement_date_pattern=r"(\d{2}\-\d{2}\-\d{4})",
        prev_balance_pattern=(
            r"(?P<description>LAST MONTH'S BALANCE?)\s+"
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_pattern=(
            r"(?P<transaction_date>\d+/\d+)\s*"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED
        ),
    )

    identifiers = [
        MetadataIdentifier(
            creator="Adobe Acrobat 23.3", producer="Adobe Acrobat Pro (64-bit)"
        )
    ]
