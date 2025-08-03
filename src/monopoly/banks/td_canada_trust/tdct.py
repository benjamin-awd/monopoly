import re

from monopoly.config import DateOrder, MultilineConfig, StatementConfig 
from monopoly.constants import (
    ISO8601,
    BankNames,
    DebitTransactionPatterns,
    CreditTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
    EntryType,
    InternalBankNames,
    SharedPatterns
)
from monopoly.constants.date import DateFormats
from monopoly.identifiers import TextIdentifier, MetadataIdentifier

from ..base import BankBase


class TDCanadaTrust(BankBase):
    name = BankNames.TDCT

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"- {ISO8601.MMM_DD}\/{DateFormats.YY}"),
        header_pattern=re.compile(r"Description.*Withdrawals.*Deposits.*Date.*Balance"),
        transaction_pattern=DebitTransactionPatterns.TDCT,
        transaction_date_format="%b%d",
        safety_check=False, # total amounts are *per page*, not overall
        transaction_auto_polarity=True
    )

    identifiers = [
        [
            # "ACCOUNT ISSUED BY: THE TORONTO\-DOMINION BANK"
            TextIdentifier(
                text="A CC\nOU\nNT\nI\nSS\nU\nED\nBY :\nTH\nE\nT\nOR\nO\nNT O-\nD\nOM\nI\nNI\nO\nN\nB\nAN\nK"
            ),
            MetadataIdentifier(
                producer='OpenText Output Transformation Engine - 23.4.00'
            ),
        ]
    ]

    statement_configs = [debit]

class TDCanadaTrustCredit(BankBase):
    name = BankNames.TDCT
    
    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"STATEMENT PERIOD.*{ISO8601.MMMM_DD_YYYY}"),
        header_pattern=re.compile(r"(TRANSACTION POSTING)"),
        prev_balance_pattern=StatementBalancePatterns.TDCT,
        transaction_pattern=CreditTransactionPatterns.TDCT,
        transaction_date_format="%b %d",
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            multiline_polarity=True
        ),
        safety_check=True,
        transaction_auto_polarity=False
    )
    identifiers = [
        [
            # TextIdentifier(
            #     text="TD CANADA TRUST"
            # ),
            MetadataIdentifier(
                producer='OpenText Output Transformation Engine - 23.4.00'
            ),
        ]
    ]

    statement_configs = [credit]

class TDCanadaTrustBusiness(BankBase):
    name = BankNames.TDCT

    debit = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"- {ISO8601.MMM_DD}\/{DateFormats.YY}"),
        header_pattern=re.compile(r"DESCRIPTION.*CHEQUE/DEBIT.*DEPOSIT/CREDIT.*DATE.*BALANCE"),
        transaction_pattern=DebitTransactionPatterns.TDCT,
        transaction_date_format="%b%d",
        safety_check=False, # total amounts are *per page*, not overall
        transaction_auto_polarity=True
    )

    identifiers = [
        [
            MetadataIdentifier(
                producer='OpenText Output Transformation Engine - 23.4.00'
            ),
            TextIdentifier(text="Accounts issued by: THE TORONTO-DOMINION BANK"),
        ]
    ]

    statement_configs = [debit]