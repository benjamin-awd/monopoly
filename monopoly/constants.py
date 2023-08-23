import os

from monopoly.enums import BankStatement, Prefix

DATE = BankStatement.DATE.value
DESCRIPTION = BankStatement.DESCRIPTION.value
AMOUNT = BankStatement.AMOUNT.value
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OCBC_365 = Prefix.OCBC_365.value
