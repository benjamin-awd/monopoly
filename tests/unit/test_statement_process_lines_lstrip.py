from monopoly.pdf import PdfPage
from monopoly.statement import Statement


def test_statement_process_lines_lstrip(statement: Statement):
    page_content = "       01-08-2023 01-09-2023\n   foo bar"

    page = PdfPage(raw_text=page_content)

    lines = statement.process_lines(page)

    expected = ["01-08-2023 01-09-2023", "foo bar"]

    assert lines == expected
