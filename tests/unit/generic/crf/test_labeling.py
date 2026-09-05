"""Unit tests for the distant-supervision labeler. Synthetic lines + gold rows only."""

from monopoly.generic.crf.labeling import GoldRow, label_line, label_page


def test_debit_line_labels_date_desc_amount_balance():
    # tokens: 01 OCT ValueVille SG 123.12 2,000.00
    gold = GoldRow(date="01 OCT", description="ValueVille SG", amount=-123.12)
    line = "01 OCT   ValueVille SG      123.12     2,000.00"
    assert label_line(line, gold) == ["DATE", "DATE", "DESC", "DESC", "AMOUNT", "BALANCE"]


def test_credit_line_single_amount_has_no_balance():
    gold = GoldRow(date="03/07", description="SAMPLE COFFEE HOUSE SG", amount=-10.0)
    line = " 03/07   SAMPLE COFFEE HOUSE   SG        10.00"
    labels = label_line(line, gold)
    assert labels[0] == "DATE"
    assert "AMOUNT" in labels
    assert "BALANCE" not in labels


def test_parenthesised_negative_amount_matches_magnitude():
    gold = GoldRow(date="02/07", description="PAYMENT BY INTERNET", amount=500.0)
    line = " 02/07   PAYMENT BY INTERNET     (500.00)"
    labels = label_line(line, gold)
    # the (500.00) token is the amount despite the sign/paren mismatch
    assert labels[-1] == "AMOUNT"


def test_trailing_sign_amount_aligns():
    # Maybank prints the sign after the amount: "120.00-"
    gold = GoldRow(date="01/08/23", description="CASH WITHDRAWAL", amount=-120.0)
    line = " 01/08/23   CASH WITHDRAWAL        120.00-        380.00"
    labels = label_line(line, gold)
    assert labels[0] == "DATE"
    assert "AMOUNT" in labels
    assert "BALANCE" in labels  # the running balance 380.00 is the second money token


def test_apostrophe_thousands_amount_aligns():
    # ZKB uses an apostrophe thousands separator: "5'200.00"
    gold = GoldRow(date="30.08.2025", description="Credit salary NORDPOL", amount=5200.0)
    line = "30.08.2025 Credit salary NORDPOL        5'200.00 30.08.2025      8'638.50"
    labels = label_line(line, gold)
    assert labels[0] == "DATE"
    assert "AMOUNT" in labels


def test_label_page_assigns_rows_to_best_lines():
    lines = [
        "STATEMENT OF ACCOUNT",
        "                LAST MONTH'S BALANCE                 500.00",
        " 02/07          PAYMENT BY INTERNET                 (500.00)",
        " 03/07          SAMPLE COFFEE HOUSE   SG              10.00",
    ]
    gold = [
        GoldRow("02/07", "LAST MONTH'S BALANCE", -500.0),
        GoldRow("02/07", "PAYMENT BY INTERNET", 500.0),
        GoldRow("03/07", "SAMPLE COFFEE HOUSE SG", -10.0),
    ]
    labeled = label_page(lines, gold)

    # header line is untouched
    assert set(labeled[0]) == {"O"}
    # balance line (no date in text) still matched via description + amount
    assert "DESC" in labeled[1] and "AMOUNT" in labeled[1]
    # both dated lines matched, and each row claimed a distinct line
    assert labeled[2][0] == "DATE" and "AMOUNT" in labeled[2]
    assert labeled[3][0] == "DATE" and "AMOUNT" in labeled[3]


def test_unmatched_gold_row_is_skipped_not_forced():
    lines = [" 03/07   SAMPLE COFFEE HOUSE   SG   10.00"]
    gold = [
        GoldRow("03/07", "SAMPLE COFFEE HOUSE SG", -10.0),
        GoldRow("99/99", "NOT ON THIS PAGE", -777.0),  # matches nothing
    ]
    labeled = label_page(lines, gold)
    # only the one real line is labeled; the phantom row does not corrupt it
    assert labeled[0][0] == "DATE"
    assert labeled[0].count("AMOUNT") == 1


def test_each_line_claimed_once():
    lines = [
        " 05/07   EXAMPLE GROCER   SG    20.00",
        " 05/07   EXAMPLE GROCER   SG    20.00",
    ]
    gold = [
        GoldRow("05/07", "EXAMPLE GROCER SG", -20.0),
        GoldRow("05/07", "EXAMPLE GROCER SG", -20.0),
    ]
    labeled = label_page(lines, gold)
    # two identical rows must claim two different lines, not the same one twice
    assert all(labels[0] == "DATE" for labels in labeled)
