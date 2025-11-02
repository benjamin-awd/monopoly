"""Store statement-related enums and constants."""

from enum import auto

from strenum import StrEnum

from monopoly.enums import AutoEnum, RegexEnum

from .date import ISO8601, DateFormats


class EntryType(AutoEnum):
    CREDIT = auto()
    DEBIT = auto()


class BankNames(AutoEnum):
    AMEX = auto()
    BANK_OF_AMERICA = auto()
    CAPITAL_ONE = auto()
    CANADIAN_TIRE = auto()
    CHASE = auto()
    CIBC = auto()
    CITIBANK = auto()
    DBS = auto()
    HSBC = auto()
    MAYBANK = auto()
    OCBC = auto()
    RBC = auto()
    SCOTIABANK = auto()
    STANDARD_CHARTERED = auto()
    UOB = auto()
    ZKB = auto()
    TRUST = auto()
    TDCT = auto()
    BMO = auto()


class InternalBankNames(AutoEnum):
    EXAMPLE = auto()
    GENERIC = auto()


class Columns(AutoEnum):
    AMOUNT = auto()
    DATE = auto()
    DESCRIPTION = auto()
    POLARITY = auto()
    TRANSACTION_DATE = auto()


class SharedPatterns(StrEnum):
    """
    Attempt to keep patterns DRY.

    AMOUNT matches the following patterns:
    1,123.12 | 123.12 | (123.12) | ( 123.12) | 123.12 CR | -1,123.12.

    AMOUNT_EXTENDED is generally used for credit statements and to
    find statement balances, while AMOUNT_EXTENDED_WITHOUT_EOL is used
    for debit statements, since debit statements have the amount + balances
    on a single line, and we only want the amount.
    """

    COMMA_FORMAT = r"\d{1,3}(,\d{3})*\.\d*"
    ENCLOSED_COMMA_FORMAT = rf"\({COMMA_FORMAT}\s{{0,1}}\))"
    OPTIONAL_NEGATIVE_SYMBOL = r"(?:-)?"
    POLARITY = r"(?P<polarity>CR\b|DR\b|DB\b|\+|\-)?\s*"

    AMOUNT = rf"(?P<amount>{COMMA_FORMAT}|{ENCLOSED_COMMA_FORMAT}\s*"
    AMOUNT_EXTENDED_WITHOUT_EOL = AMOUNT + POLARITY
    AMOUNT_EXTENDED = AMOUNT_EXTENDED_WITHOUT_EOL + r"$"

    BALANCE = rf"(?P<balance>{COMMA_FORMAT})?$"
    DESCRIPTION = r"(?P<description>.*?)\s+"
    TRANSACTION_DATE_ABBREVIATED_ALL_CAPS = r"(?P<transaction_date>\d{2}\s[A-Z]{3})\s+"
    TRANSACTION_DATE_ABBREVIATED_PROPER_CASE = r"(?P<transaction_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"
    POSTING_DATE_ABBREVIATED_PROPER = r"(?P<posting_date>\d{2}\s[A-Z]{1}[a-z]{2})\s+"


class StatementBalancePatterns(RegexEnum):
    DBS = r"(?P<description>PREVIOUS BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    CITIBANK = r"(?P<description>BALANCE PREVIOUS STATEMENT?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    HSBC = r"(?P<description>Previous Statement Balance?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    MAYBANK_MY = r"(?P<description>YOUR PREVIOUS STATEMENT BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    MAYBANK_SG = (
        r"(?P<description>OUTSTANDING\s+BALANCE\s+BROUGHT\s+FORWARD?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    OCBC = r"(?P<description>LAST MONTH'S BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    STANDARD_CHARTERED = (
        r"(?P<description>BALANCE FROM PREVIOUS STATEMENT?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    UOB = r"(?P<description>PREVIOUS BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    TRUST = r"(?P<description>Previous balance?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    TDCT = r"(?P<description>PREVIOUS STATEMENT BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    RBC = r"(?P<description>PREVIOUS STATEMENT BALANCE?)\s+" + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    CIBC = (
        r"(?P<description>Previous balance?)\s+"
        rf"(?P<amount>{SharedPatterns.OPTIONAL_NEGATIVE_SYMBOL}\$?{SharedPatterns.COMMA_FORMAT})"
    )


class CreditTransactionPatterns(RegexEnum):
    AMEX_PLATINUM = (
        rf"(?P<transaction_date>{ISO8601.DD_MM_YY})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    )
    BANK_OF_AMERICA = (
        rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
        rf"(?P<posting_date>{ISO8601.MM_DD})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?P<reference_number>\d{4})?\s+"
        + r"(?P<account_number>\d{4})?\s+"
        + r"(?P<polarity>\-)?"
        + SharedPatterns.AMOUNT
    )
    BMO = (
        r"(?P<transaction_date>[A-Z][a-z]{2,3}\.\s+\d{1,2})\s+"
        r"(?P<posting_date>[A-Z][a-z]{2,3}\.\s+\d{1,2})\s+"
        r"(?P<description>.+?)\s+"
        r"(?P<amount>\d{1,3}(?:,\d{3})*\.\d{2})(\s+)?"
        r"(?P<polarity>CR)?$"
    )
    DBS = rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    CANADIAN_TIRE = (
        r"^\s*"
        r"(?P<transaction_date>[A-Z][a-z]{2}\s\d{2})\s+"
        r"(?P<posting_date>[A-Z][a-z]{2}\s\d{2})\s+"
        r"(?!\s*\d+\b)"
        r"(?P<description>.+?)\s{2,}"  # NOTE: no way to not parse trailing text in line as description?
        r"(?P<polarity>-)"
        r"?(?P<amount>\d{1,3}(?:,\d{3})*\.\d{2})"
    )
    CAPITAL_ONE = (
        r"^\s*"
        rf"(?P<transaction_date>\b({DateFormats.MMM}\s+{DateFormats.D}))\s+"
        rf"(?P<posting_date>\b({DateFormats.MMM}\s+{DateFormats.D}))\s+"
        f"{SharedPatterns.DESCRIPTION}"
        rf"(?P<polarity>-)?\s*\$"
        rf"(?P<amount>{SharedPatterns.COMMA_FORMAT})\s*$"
    )
    CHASE = (
        rf"(?P<transaction_date>{ISO8601.MM_DD})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?P<polarity>\-)?"
        + r"(?P<amount>(\d{1,3}(,\d{3})*|\d*)\.\d+)$"
    )
    CIBC = (
        rf"(?P<transaction_date>\b({DateFormats.MMM}[-\s]{DateFormats.DD}))\s+"
        rf"(?P<posting_date>\b({DateFormats.MMM}[-\s]{DateFormats.DD}))\s+"
        r"(?:Ý\s*)?(?P<description>.+?)\s{2,}"
        r"(?P<catagory>.*?)\s+"
        # transaction dr/cr with format -$999,000.00
        rf"(?P<amount>{SharedPatterns.OPTIONAL_NEGATIVE_SYMBOL}\$?{SharedPatterns.COMMA_FORMAT}|{SharedPatterns.ENCLOSED_COMMA_FORMAT}\s*"
    )
    CITIBANK = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    )
    HSBC = (
        rf"(?P<posting_date>{ISO8601.DD_MMM_RELAXED})\s+"
        rf"(?P<transaction_date>{ISO8601.DD_MMM_RELAXED})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    MAYBANK_SG = (
        r"(?P<posting_date>\b[A-Z]?\d{1,2}(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b)\s+"
        r"(?P<transaction_date>\b[A-Z]?\d{1,2}(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b)\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED
    )
    MAYBANK_MY = (
        rf"(?P<posting_date>{ISO8601.DD_MM})\s+"
        rf"(?P<transaction_date>{ISO8601.DD_MM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    )
    OCBC = r"(?P<transaction_date>\d+/\d+)\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    RBC = (
        rf"(?P<transaction_date>\b({DateFormats.MMM}[-\s]{DateFormats.DD}))\s+"
        rf"(?P<posting_date>\b({DateFormats.MMM}[-\s]{DateFormats.DD}))\s+"
        + SharedPatterns.DESCRIPTION
        # transaction dr/cr with format -$999,000.00
        + r"(?P<polarity>\-)?"
        + rf"(?P<amount>\$?{SharedPatterns.COMMA_FORMAT}|{SharedPatterns.ENCLOSED_COMMA_FORMAT}\s*"
    )
    SCOTIABANK = (
        rf"(?P<transaction_date>\b({DateFormats.MMM}[\/\-\s.]{DateFormats.D}))\s+"
        rf"(?P<posting_date>\b({DateFormats.MMM}[\/\-\s.]{DateFormats.D}))\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL  # "credits" are denoted at the end of the amount, i.e PMYT 155.96-
    )
    STANDARD_CHARTERED = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?:(?P<transaction_ref>Transaction\sRef\s\d+)?)\s+"
        + SharedPatterns.AMOUNT_EXTENDED
    )
    UOB = (
        rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+" + SharedPatterns.DESCRIPTION + SharedPatterns.AMOUNT_EXTENDED
    )
    TDCT = (
        rf"(?P<transaction_date>\b({DateFormats.MMM}[-\s]{DateFormats.D}))\s+"
        rf"(?P<posting_date>\b({DateFormats.MMM}[-\s]{DateFormats.D}))\s+"
        + SharedPatterns.DESCRIPTION
        # transaction dr/cr with format -$999,000.00
        + rf"(?P<amount>{SharedPatterns.OPTIONAL_NEGATIVE_SYMBOL}\$?{SharedPatterns.COMMA_FORMAT})\s*"
    )
    TRUST = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        r"(?P<description>(?:(?!Total outstanding balance).)*?)"
        r"(?P<polarity>\+)?"
        f"{SharedPatterns.AMOUNT}"
        r"$"  # necessary to ignore FCY
    )


class DebitTransactionPatterns(RegexEnum):
    BANK_OF_AMERICA = (
        rf"(?P<transaction_date>{ISO8601.MM_DD_YY})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?P<polarity>\-)?"
        + SharedPatterns.AMOUNT
    )
    BMO = (
        rf"^(?!.*(?:Closing totals)).*?"
        rf"(?P<transaction_date>{ISO8601.MMM_DD})\s+"
        rf"{SharedPatterns.DESCRIPTION}\s+"
        rf"(?P<amount>{SharedPatterns.COMMA_FORMAT})\s+"
        rf"(?P<balance>{SharedPatterns.COMMA_FORMAT})$"
    )
    CIBC = (
        rf"\s*(?:(?P<transaction_date>{DateFormats.MMM}\s+{DateFormats.D})[-\s]+)?"
        r"(?P<description>(?!(Deposits)).+?)\s{2,}"
        rf"(?P<amount>{SharedPatterns.COMMA_FORMAT})"
        rf"[-\s]+(?P<balance>{SharedPatterns.OPTIONAL_NEGATIVE_SYMBOL}\$?{SharedPatterns.COMMA_FORMAT})"
    )
    DBS = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    DBS_POSB_CONSOLIDATED = (
        rf"(?P<transaction_date>{ISO8601.DD_MM_YYYY})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
    )
    MAYBANK_MY = (
        rf"(?P<transaction_date>{ISO8601.DD_MM_YY})\s+"
        + SharedPatterns.DESCRIPTION
        # remove *\s
        + SharedPatterns.AMOUNT[:-3]
        + r"(?P<polarity>\-|\+)\s+"
        + SharedPatterns.BALANCE
    )
    OCBC = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        rf"(?P<posting_date>{ISO8601.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        + SharedPatterns.BALANCE
    )
    RBC = (
        r"^(?!.*(?:Opening Balance|Closing Balance))"
        r"(\s*)?"
        rf"(?P<transaction_date>{DateFormats.D}\s+{DateFormats.MMM})?\s+"  # i.e 7 May
        r"(?P<description>.+?)\s{2,}"
        rf"(?P<amount>{SharedPatterns.COMMA_FORMAT})"
        r"(?:\s{2,}(?P<balance>-?\s?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})))?"  # edge case for literally "- 100.00"
        r"\s*$"
    )
    SCOTIABANK = (
        r"^(?!.*(?:Opening Balance)).*?"  # avoid matching opening balance as a "transaction"
        rf"(?P<transaction_date>{ISO8601.MMM_DD})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT
        + SharedPatterns.BALANCE
    )
    UOB = (
        rf"(?P<transaction_date>{ISO8601.DD_MMM})\s+"
        + SharedPatterns.DESCRIPTION
        + SharedPatterns.AMOUNT_EXTENDED_WITHOUT_EOL
        + SharedPatterns.BALANCE
    )
    ZKB = (
        rf"(?P<transaction_date>{ISO8601.DD_MM_YYYY})\s+"
        + SharedPatterns.DESCRIPTION
        + r"(?P<amount>\d{1,3}(\'\d{3})*(\.\d+)?)\s+"
        + rf"(?P<value_date>{ISO8601.DD_MM_YYYY})\s+"
        + r"(?P<balance>\d{1,3}(\'\d{3})*(\.\d+)?)$"
    )
    TDCT = (
        SharedPatterns.DESCRIPTION
        + rf"(?P<amount>{SharedPatterns.COMMA_FORMAT})"
        + rf"[-\s]+(?P<transaction_date>\b({DateFormats.MMM}{DateFormats.DD}))"  # i.e MAY1 and MAY27
        + rf"([-\s]+(?P<balance>{SharedPatterns.COMMA_FORMAT}))?"  # balance is shown at end of each day
    )
