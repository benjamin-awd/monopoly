from monopoly.banks.base import BankBase
from monopoly.config import StatementConfig, TransactionConfig
from monopoly.constants import AccountType, BankNames, SharedPatterns


class MonopolyBank(BankBase):
    """Dummy class to help with reading the example PDF statement"""

    statement_config = StatementConfig(
        bank_name=BankNames.EXAMPLE,
        account_type=AccountType.CREDIT,
        date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        date_format=r"%d-%m-%Y",
        prev_balance_pattern=(
            r"(?P<description>LAST MONTH'S BALANCE?)\s+" + SharedPatterns.AMOUNT
        ),
    )

    transaction_config = TransactionConfig(
        pattern=(
            r"(?P<transaction_date>\d+/\d+)\s*"
            r"(?P<description>.*?)\s*" + SharedPatterns.AMOUNT
        ),
        date_format=r"%d/%m",
    )
