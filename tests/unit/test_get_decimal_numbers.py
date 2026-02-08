from monopoly.statements.number_extractor import NumberExtractor


def test_get_decimal_numbers():
    lines = [
        "These are some sample lines 123.45 and 67.89",
        "Another line with a decimal number 0.56 but not here 123",
        "No decimals in this line 45, maybe here 10.0 or not",
    ]

    expected_decimal_numbers = {123.45, 67.89, 0.56, 10.0}

    extractor = NumberExtractor(pages=[])
    decimal_numbers = extractor._get_decimal_numbers(lines)

    assert decimal_numbers == expected_decimal_numbers
