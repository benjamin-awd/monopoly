import re

from monopoly.banks import Hsbc, Ocbc
from monopoly.config import MultilineConfig
from monopoly.pdf import PdfPage
from monopoly.statements import BaseStatement
from monopoly.statements.base import MatchContext
from monopoly.statements.transaction import (
    Transaction,
    TransactionGroupDict,
    TransactionMatch,
)


def test_get_transactions(statement: BaseStatement):
    pattern = Ocbc.credit.transaction_pattern
    statement.config.transaction_pattern = pattern

    statement.pages = [PdfPage("19/06 YA KUN KAYA TOAST 3.20\n20/06 FAIRPRICE FINEST 9.90")]
    transactions = statement.get_transactions()
    expected = [
        Transaction(
            transaction_date="19/06",
            description="YA KUN KAYA TOAST",
            amount=-3.2,
            polarity=None,
        ),
        Transaction(
            transaction_date="20/06",
            description="FAIRPRICE FINEST",
            amount=-9.9,
            polarity=None,
        ),
    ]
    assert transactions == expected


def test_check_bound(statement: BaseStatement):
    pattern = Ocbc.credit.transaction_pattern
    statement.config.transaction_pattern = pattern
    statement.config.transaction_bound = 30

    statement.pages = [PdfPage("19/06 YA KUN KAYA TOAST 3.20\n20/06 FAIRPRICE FINEST             9.90")]
    transactions = statement.get_transactions()
    expected = [
        Transaction(
            transaction_date="19/06",
            description="YA KUN KAYA TOAST",
            amount=-3.2,
            polarity=None,
        ),
    ]
    statement.config.transaction_bound = None
    assert transactions == expected


def test_get_multiline_descriptions(statement: BaseStatement):
    pattern = Hsbc.credit.transaction_pattern
    statement.config.multiline_config = MultilineConfig(True)
    statement.config.transaction_pattern = pattern
    statement.pages = [PdfPage("04 Aug 02 Aug SHOPEE 3.20\n              CCY FEE 1.25\n              SINGAPORE SG")]
    transactions = statement.get_transactions()
    expected = [
        Transaction(
            transaction_date="02 Aug",
            description="SHOPEE CCY FEE 1.25 SINGAPORE SG",
            amount=-3.2,
            polarity=None,
        )
    ]
    assert transactions == expected


def test_process_match_multiline_description(statement: BaseStatement):
    pattern = Hsbc.credit.transaction_pattern
    statement.config.multiline_config = MultilineConfig(True)
    statement.config.transaction_pattern = pattern

    groupdict = {
        "transaction_date": "04 Aug",
        "description": "SHOPEE",
        "amount": "3.20",
        "polarity": None,
    }
    match = TransactionMatch(
        match=re.search("foo", "foo"),
        groupdict=TransactionGroupDict(**groupdict),
        page_number=0,
    )

    # case 1: transaction is found on next line
    line = "04 Aug 02 Aug SHOPEE 3.20"
    lines = ["04 Aug 02 Aug SHOPEE 3.20", "05 Aug 02 Aug ValueVille 3.20"]
    expected_groupdict = {
        "transaction_date": "04 Aug",
        "amount": "3.20",
        "description": "SHOPEE",
        "polarity": None,
    }
    context = MatchContext(line=line, lines=lines, idx=0, description="SHOPEE")
    match = statement.process_match(match, context)
    assert match.groupdict.asdict() == expected_groupdict

    # case 2: description across next line is more than three spaces apart
    line = "04 Aug 02 Aug SHOPEE 3.20"
    lines = ["04 Aug 02 Aug SHOPEE 3.20", "foo", "bar"]
    context = MatchContext(line=line, lines=lines, idx=0, description="SHOPEE")
    assert match.groupdict.asdict() == groupdict
