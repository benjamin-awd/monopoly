from monopoly.banks.base import BankBase
from monopoly.config import CreditStatementConfig
from monopoly.constants import InternalBankNames, SharedPatterns
from monopoly.identifiers import TextIdentifier


class ExampleBank(BankBase):
    """Dummy class to help with reading the example PDF statement"""

    credit_config = CreditStatementConfig(
        bank_name=InternalBankNames.EXAMPLE,
        statement_date_pattern=r"(\d{2}\-\d{2}\-\d{4})",
        header_pattern=r"(DATE.*DESCRIPTION.*AMOUNT)",
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
        [
            TextIdentifier(text="HCBS12345(12345)"),
        ]
    ]
