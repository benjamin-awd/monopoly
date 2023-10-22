from monopoly.banks.base import BankBase
from monopoly.config import StatementConfig
from monopoly.constants import AccountType, BankNames


# fmt: off
class MonopolyBank(BankBase):
    """Dummy class to help with reading the example PDF statement"""
    statement_config = StatementConfig(
        bank_name="monopoly",
        account_type=AccountType.CREDIT,
        transaction_pattern=(
            r"(?P<date>\d+/\d+)\s*"
            r"(?P<description>.*?)\s*"
            r"(?P<amount>[\d.,]+)$"
        ),
        transaction_date_format=r"%d/%m",
        statement_date_pattern=r"\d{2}\-\d{2}\-\d{4}",
        statement_date_format=r"%d-%m-%Y",
    )

    pdf_config = None
