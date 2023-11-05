from monopoly.banks.base import BankBase
from monopoly.config import StatementConfig, TransactionConfig
from monopoly.constants import AccountType, BankNames


# fmt: off
class MonopolyBank(BankBase):
    """Dummy class to help with reading the example PDF statement"""
    statement_config = StatementConfig(
        bank_name=BankNames.EXAMPLE,
        account_type=AccountType.CREDIT,
        statement_date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        statement_date_format=r"%d-%m-%Y",
    )

    transaction_config = TransactionConfig(
        pattern=(
            r"(?P<transaction_date>\d+/\d+)\s*"
            r"(?P<description>.*?)\s*"
            r"(?P<amount>[\d.,]+)$"
        ),
        date_format=r"%d/%m",
    )
