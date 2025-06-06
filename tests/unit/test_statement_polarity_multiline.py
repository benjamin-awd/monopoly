from monopoly.statements.base import BaseStatement, MatchContext


def test_multiline_polarity_detected(statement: BaseStatement):
    statement.pages[0].lines = [
        "24.02.25  PAYMENT RECEIVED - THANK YOU            79.99",
        "                                                  CR",
    ]

    context = MatchContext(
        lines=statement.pages[0].lines,
        line=statement.pages[0].lines[0],
        description="PAYMENT RECEIVED - THANK YOU",
        idx=0,
    )

    result = statement.get_multiline_polarity(context)
    assert result == "CR"
