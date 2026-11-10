"""
Tests for the HDFC credit card transaction pattern.

pdftotext renders the rupee glyph as "C" and the trailing purchase-indicator
bullet as "l". Merchants below are made up.
"""

from monopoly.banks import Hdfc
from monopoly.pdf import PdfPage
from monopoly.statements import CreditStatement

pattern = Hdfc.credit.transaction_pattern


def parse(*lines: str):
    page = PdfPage(raw_text="\n".join(lines))
    return CreditStatement([page], Hdfc.name, Hdfc.credit, "header").get_transactions()


def test_lakh_grouped_amount_is_read_whole():
    line = "23/05/2026| 18:44            EXAMPLE JEWELLERSMUMBAI           + 1234    C 1,23,456.78    l"
    match = pattern.search(line)
    assert match is not None
    assert match.group("amount") == "1,23,456.78"
    assert parse(line)[0].amount == -123456.78


def test_reward_points_are_not_a_credit_marker():
    spaced, tight = parse(
        "23/05/2026| 18:44            EXAMPLE STOREGURGAON              + 30        C 978.00    l",
        "26/05/2026| 11:20            WWW EXAMPLE INBANGALORE            +5         C 283.00    l",
    )
    assert (spaced.description, spaced.amount, spaced.direction) == ("EXAMPLE STOREGURGAON", -978.00, "debit")
    assert (tight.description, tight.amount, tight.direction) == ("WWW EXAMPLE INBANGALORE", -283.00, "debit")


def test_plus_before_the_rupee_glyph_is_a_credit():
    (payment,) = parse(
        "27/05/2026| 11:27            BPPY CC PAYMENT (Ref# ST0000000000)                + C 19,155.00   l"
    )
    assert payment.description == "BPPY CC PAYMENT (Ref# ST0000000000)"
    assert payment.amount == 19155.00
    assert payment.direction == "credit"


def test_emi_flag_is_not_part_of_the_description():
    (row,) = parse("31/05/2026| 16:40    EMI     EXAMPLE SPIRITSBANGALORE          + 150     C 4,555.00    l")
    assert row.description == "EXAMPLE SPIRITSBANGALORE"
    assert row.amount == -4555.00


def test_international_row_takes_the_rupee_amount():
    (row,) = parse("10/05/2026 | 12:12           EXAMPLE* SAASNEW YORK       USD 15.00   + 45      C 1,442.14    l")
    assert row.date == "10/05/2026"
    assert row.description == "EXAMPLE* SAASNEW YORK USD 15.00"
    assert row.amount == -1442.14


def test_amount_only_row_still_counts():
    (row,) = parse("12/05/2026 | 00:00                                                           C 5.19    l")
    assert row.description == ""
    assert row.amount == -5.19


def test_description_wrapped_around_its_row_is_joined():
    """Fee and tax rows print their description on the lines above and below."""
    saas, tax, markup = parse(
        "10/05/2026 | 12:12           EXAMPLE* SAASNEW YORK       USD 15.00   + 45      C 1,442.14    l",
        "                             TAX-EX0000000000001-RATE 18.0 -29 (Ref#",
        "12/05/2026 | 00:00                                                           C 5.19    l",
        "                             AB000000000000000000001)",
        "                             EXAMPLE FCY MARKUP FEE (Ref#",
        "09/06/2026 | 00:00                                                          C 28.84    l",
        "                             AB000000000000000000001)",
        "",
        "*Transaction time captured in IST Zone.",
    )
    assert saas.description == "EXAMPLE* SAASNEW YORK USD 15.00"
    assert (tax.description, tax.amount) == ("TAX-EX0000000000001-RATE 18.0 -29 (Ref# AB000000000000000000001)", -5.19)
    assert (markup.description, markup.amount) == ("EXAMPLE FCY MARKUP FEE (Ref# AB000000000000000000001)", -28.84)


def test_summary_lines_are_not_transactions():
    assert pattern.search("Statement Date   09 Jun, 2026        TOTAL AMOUNT DUE") is None
    assert pattern.search("              C19,155.43") is None
