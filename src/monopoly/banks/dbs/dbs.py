import re

from monopoly.banks.base import BankBase
from monopoly.config import MultilineConfig, PaymentSummaryConfig, StatementConfig
from monopoly.constants import EntryType, SharedPatterns
from monopoly.constants.date import ISO8601
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class Dbs(BankBase):
    name = "dbs"

    credit = StatementConfig(
        currency="SGD",
        statement_type=EntryType.CREDIT,
        statement_date_pattern=ISO8601.DD_MMM_YYYY.regex,
        # card number in the header block, e.g. "... CARD NO.: 4111 2222 3333 4444"
        account_pattern=re.compile(r"(?i)CARD NO\.:\s*(?P<account>\d{4}(?:\s+\d{4}){3})"),
        header_pattern=re.compile(r"(DATE.*DESCRIPTION.*AMOUNT)"),
        transaction_date_format="%d %b",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
        ),
        prev_balance_pattern=re.compile(
            r"(?P<description>PREVIOUS BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        payment_summary_config=PaymentSummaryConfig(
            # top summary row: "15 Oct 2023   $25,000.00   $509.08   09 Nov 2023"
            #                  (statement date, credit limit, min payment, due date)
            payment_due_date=re.compile(
                r"\d{1,2}\s+\w{3}\s+\d{4}\s+\$[\d,]+\.\d{2}\s+\$[\d,]+\.\d{2}\s+"
                r"(?P<due_date>\d{1,2}\s+\w{3}\s+\d{4})"
            ),
            # payment coupon: "TOTAL   $ 16,969.17   $ 509.08"
            total_amount_due=re.compile(
                r"TOTAL\s+\$\s*(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")\s+\$\s*[\d,]+\.\d{2}"
            ),
            minimum_payment=re.compile(
                r"TOTAL\s+\$\s*[\d,]+\.\d{2}\s+\$\s*(?P<amount>" + SharedPatterns.COMMA_FORMAT + r")"
            ),
        ),
    )

    debit = StatementConfig(
        currency="SGD",
        statement_type=EntryType.DEBIT,
        statement_date_pattern=ISO8601.DD_MMM_YYYY.regex,
        # account number in the header block, e.g. "Account No.: 098-7-654321"
        account_pattern=re.compile(r"(?i)Account No\.:\s*(?P<account>[\d-]+)"),
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            description_margin=10,  # Allow for indented PayNow/transaction details
        ),
        header_pattern=re.compile(r"(WITHDRAWAL.*DEPOSIT.*BALANCE)"),
        transaction_date_format="%d %b",
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
            + SharedPatterns.DESCRIPTION
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        transaction_bound=170,
    )

    consolidated = StatementConfig(
        currency="SGD",
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"Details as at {ISO8601.DD_MMM_YYYY}"),
        # each account's table opens with "DBS Multiplier Account   Account No. 123-456789-0" on every
        # page. The account summary above the tables can print the number truncated, so it isn't used.
        account_pattern=re.compile(r"Account No\.\s*(?P<account>\d{3}-\d{1,6}-\d{1,6})"),
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            description_margin=10,  # Allow for indented PayNow/transaction details
        ),
        header_pattern=re.compile(r"(\s*Date\s+Description\s+Withdrawal.*)"),
        transaction_date_format="%d/%m/%Y",
        # The description must not be empty: the closing line of an account ("30/06/2023 ... 20.66")
        # has a date and its balance only, which would otherwise read as a deposit of that balance.
        transaction_pattern=re.compile(
            rf"(?P<transaction_date>{ISO8601.DD_MM_YYYY})\s+(?P<description>\S.*?)\s+"
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
        # Later pages of a consolidated statement indent the table further right
        # than the first page (Balance column drifts 210 -> 223 -> 234), pushing
        # the withdrawal/deposit amount column to col 223 on some pages. 230 keeps
        # those real amounts while still rejecting balance-only summary lines,
        # whose amounts land at col 239+.
        transaction_bound=230,
    )

    # DBS/POSB consolidated statements issued before mid-2021 were rendered by StreamServe: each account's
    # table has a "Date Description Withdrawal Deposit Balance" header (no "(-)"/"(+)" markers) and "03 Jun"
    # dates. They also carry a debit card summary whose "DATE DESCRIPTION ... AMOUNT" header would match the
    # credit config, so this config is tried first; its header doesn't occur in any other DBS layout.
    consolidated_legacy = StatementConfig(
        currency="SGD",
        statement_type=EntryType.DEBIT,
        statement_date_pattern=re.compile(rf"As at {ISO8601.DD_MMM_YYYY}"),
        # each account's table opens with "<account name>   Account No. 123-456789-0"
        account_pattern=re.compile(r"Account No\.\s*(?P<account>\d{3}-\d{1,6}-\d{1,6})"),
        multiline_config=MultilineConfig(
            multiline_descriptions=True,
            description_margin=10,
        ),
        header_pattern=re.compile(r"(Date\s+Description\s+Withdrawal\s+Deposit\s+Balance)"),
        transaction_date_format="%d %b",
        # Account rows are dated in title case ("03 Jun"); the debit card summary that follows the accounts
        # prints its months in capitals ("31 MAY") and lists card spending already in the accounts, so
        # matching title-case months only keeps it out.
        transaction_pattern=re.compile(
            r"\b"
            + SharedPatterns.TRANSACTION_DATE_ABBREVIATED_PROPER_CASE
            + r"(?P<description>\S.*?)\s+"
            + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        ),
    )

    identifiers = [
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="Quadient CXM AG"),
        ],
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="Quadient"),
        ],
        # Statements issued before mid-2021 were rendered by StreamServe, with creator "DBS"
        [
            TextIdentifier("DBS"),
            MetadataIdentifier(creator="DBS", producer="StreamServe"),
        ],
        # ...and DBS/POSB consolidated statements of that time, whose creator is empty
        [
            TextIdentifier("DBS Bank Ltd"),
            TextIdentifier("CONSOLIDATED STATEMENT"),
            MetadataIdentifier(producer="StreamServe"),
        ],
    ]

    statement_configs = [consolidated_legacy, credit, consolidated, debit]
