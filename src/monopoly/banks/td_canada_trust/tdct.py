import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, StatementConfig
from monopoly.constants import (
    ISO8601,
    BankNames,
    CreditTransactionPatterns,
    DebitTransactionPatterns,
    EntryType,
    StatementBalancePatterns,
)
from monopoly.constants.date import DateFormats
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class TDCanadaTrust(BankBase):
    name = BankNames.TDCT

    debit_personal = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"- {ISO8601.MMM_DD}\/{DateFormats.YY}"),
        header_pattern=re.compile(r"Description.*Withdrawals.*Deposits.*Date.*Balance"),
        transaction_pattern=DebitTransactionPatterns.TDCT,
        transaction_date_format="%b%d",
        safety_check=False,  # total amounts are *per page*, not overall
        transaction_auto_polarity=True,
    )

    debit_business = StatementConfig(
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"- {ISO8601.MMM_DD}\/{DateFormats.YY}"),
        header_pattern=re.compile(r"DESCRIPTION.*CHEQUE/DEBIT.*DEPOSIT/CREDIT.*DATE.*BALANCE"),
        transaction_pattern=DebitTransactionPatterns.TDCT,
        transaction_date_format="%b%d",
        safety_check=False,  # total amounts are *per page*, not overall
        transaction_auto_polarity=True,
    )

    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        statement_date_pattern=re.compile(rf"STATEMENT PERIOD.*{ISO8601.MMMM_DD_YYYY}"),
        header_pattern=re.compile(r"(TRANSACTION\s+POSTING)"),
        prev_balance_pattern=StatementBalancePatterns.TDCT,
        transaction_pattern=CreditTransactionPatterns.TDCT,
        transaction_date_format="%b %d",
        multiline_config=MultilineConfig(multiline_descriptions=True, multiline_polarity=True),
        transaction_auto_polarity=False,
    )

    identifiers = [
        # DR personal
        [
            MetadataIdentifier(producer="OpenText Output Transformation Engine -"),
            # ACCOUNT ISSUED BY: THE TORONTO\-DOMINION BANK
            TextIdentifier(
                text="A CC\nOU\nNT\nI\nSS\nU\nED\nBY :\nTH\nE\nT\nOR\nO\nNT O-\nD\nOM\nI\nNI\nO\nN\nB\nAN\nK"
            ),
        ],
        # DR business
        [
            MetadataIdentifier(producer="OpenText Output Transformation Engine -"),
            TextIdentifier(text="Accounts issued by: THE TORONTO-DOMINION BANK"),
        ],
        # CR
        [
            MetadataIdentifier(producer="OpenText Output Transformation Engine -"),
            TextIdentifier(text="TDSTM"),
        ],
    ]

    statement_configs = [debit_personal, debit_business, credit]
