from monopoly.constants import TransactionPatterns
from monopoly.statement import Statement, Transaction


def test_process_line(statement: Statement):
    statement.config.transaction_pattern = TransactionPatterns.OCBC
    line = "19/06 YA KUN KAYA TOAST 3.20"
    lines = ["19/06 YA KUN KAYA TOAST 3.20", "20/06 FAIRPRICE FINEST 9.90"]
    idx = 0
    transaction = statement._process_line(line, lines, idx)
    assert transaction == Transaction("19/06", "YA KUN KAYA TOAST", 3.2)


def test_process_line_no_match(statement: Statement):
    statement.config.transaction_pattern = "foobar"
    line = "Invalid line"
    lines = ["Invalid line"]
    idx = 0
    transaction = statement._process_line(line, lines, idx)
    assert transaction is None


def test_process_line_multiline_description(statement: Statement):
    statement.config.transaction_pattern = TransactionPatterns.HSBC
    statement.config.multiline_transactions = True
    line = "04 Aug 02 Aug SHOPEE 3.20"
    lines = ["04 Aug 02 Aug SHOPEE 3.20", "SINGAPORE SG"]
    idx = 0
    transaction = statement._process_line(line, lines, idx)
    assert transaction == Transaction("02 Aug", "SHOPEE SINGAPORE SG", 3.2)
