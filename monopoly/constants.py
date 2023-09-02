import os

from monopoly.enums import BankStatement, EmailSubject

DATE = BankStatement.DATE.value
DESCRIPTION = BankStatement.DESCRIPTION.value
AMOUNT = BankStatement.AMOUNT.value
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OCBC_365 = EmailSubject.OCBC_365.value
HSBC_REVOLUTION = EmailSubject.HSBC_REVOLUTION.value
