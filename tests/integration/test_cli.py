import os
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from monopoly.cli.models import Report, Result
from monopoly.cli import (
    get_statement_paths,
    monopoly,
    pprint_transactions,
)
from monopoly.statements.transaction import Transaction


@pytest.fixture
def mock_results():
    result1 = Result(source_file_name="statement1.pdf", target_file_name="processed1.csv")
    result2 = Result(
        source_file_name="statement2.pdf",
        error_info={
            "message": "Error",
            "traceback": "Traceback (most recent call last)",
        },
    )
    return [result1, result2]


@pytest.fixture
def test_directory() -> Path:
    return Path("tests/integration/test_cli").resolve()


@pytest.fixture
def cli_runner():
    yield CliRunner()


def test_display_report(mock_results, capsys):
    report = Report(results=mock_results)
    report.display_report()
    captured = capsys.readouterr()
    printed_output = captured.out.strip().split("\n")

    assert "1 statement(s) had errors while processing" in printed_output
    assert "1 statement(s) processed" in printed_output
    assert "statement1.pdf -> processed1.csv" in printed_output
    assert "statement2.pdf -- Error" in printed_output

    # Test verbose output
    report.display_report(verbose=True)
    captured = capsys.readouterr()
    printed_output = captured.out.strip().split("\n")
    assert "statement2.pdf -- Traceback (most recent call last)" in printed_output


def test_help_command() -> None:
    cli_runner = CliRunner()
    help_results = cli_runner.invoke(monopoly, args="--help")
    assert help_results.exit_code == 0
    assert help_results.stdout.startswith("Usage: monopoly")


def test_monopoly_output(cli_runner: CliRunner):
    with open("src/monopoly/examples/example_statement.pdf", "rb") as source_file:
        file_content = source_file.read()

    with cli_runner.isolated_filesystem() as tmp_dir:
        with open(f"{tmp_dir}/input.pdf", "wb") as destination_file:
            destination_file.write(file_content)

        result_dir = "results"
        os.mkdir(result_dir)
        result = cli_runner.invoke(monopoly, [".", "--output", f"{tmp_dir}/{result_dir}"])

        assert result.exit_code == 0
        assert "1 statement(s) processed" in result.output
        assert "input.pdf -> example-credit-2023-07-74498f.csv\n" in result.output


def test_monopoly_pprint(cli_runner: CliRunner):
    result = cli_runner.invoke(monopoly, ["src/monopoly/examples/example_statement.pdf", "--pprint"])

    assert result.exit_code == 0
    expected_output = (
        "example_statement.pdf\n"
        "+------------+-----------------------------------+----------+\n"
        "| date       | description                       |   amount |\n"
        "|------------+-----------------------------------+----------|\n"
        "| 2023-07-02 | LAST MONTH'S BALANCE              |  -412.16 |\n"
        "| 2023-07-02 | PAYMENT BY INTERNET               |   412.16 |\n"
        "| 2023-07-03 | DELIGHTFUL BREAKFAST SINGAPORE SG |     -4.2 |\n"
        "| 2023-07-06 | URBAN TRANSIT CO. SINGAPORE SG    |    -1.38 |\n"
        "| 2023-07-07 | MORNING BITES CAFE SINGAPORE SG   |     -4.2 |\n"
        "| 2023-07-13 | SUNRISE TOAST HAVEN SINGAPORE SG  |     -3.2 |\n"
        "| 2023-07-15 | ARCTIC MARKET SINGAPORE SG        |       -7 |\n"
        "| 2023-07-16 | SPEEDY DRIVE SHOP SINGAPORE SG    |    -11.9 |\n"
        "| 2023-07-16 | TRAVELEATS EXPRESS SINGAPORE SG   |       -1 |\n"
        "| 2023-07-17 | FROSTED PANTRY SINGAPORE SG       |    -2.51 |\n"
        "| 2023-07-18 | COMMUTE & GO MART SINGAPORE SG    |     -9.9 |\n"
        "| 2023-07-18 | CULINARY CONNECT SINGAPORE SG     |    -6.95 |\n"
        "| 2023-07-18 | NATURE'S OVEN SINGAPORE SG        |    -1.29 |\n"
        "| 2023-07-18 | CHILLED URBAN MART SINGAPORE SG   |    -2.64 |\n"
        "| 2023-07-19 | GLOBAL FLAVORS SINGAPORE SG       |     -5.5 |\n"
        "| 2023-07-19 | FITLIFE ACCESS SINGAPORE SG       |    -17.4 |\n"
        "| 2023-07-20 | MORNING BITE CAFE SINGAPORE SG    |     -8.3 |\n"
        "| 2023-07-20 | FOODIE EXPRESS SINGAPORE 239 SG   |   -36.25 |\n"
        "| 2023-07-20 | GASTRONOMIC OASIS SINGAPORE SG    |    -2.28 |\n"
        "| 2023-07-21 | TRANQUIL TRANSIT SINGAPORE SG     |    -11.9 |\n"
        "| 2023-07-21 | URBAN HARVEST SINGAPORE SG        |     -7.3 |\n"
        "| 2023-07-21 | ENCHANTED CAFE SINGAPORE SG       |    -11.9 |\n"
        "| 2023-07-22 | FROZEN WONDERS SINGAPORE SG       |     -6.1 |\n"
        "| 2023-07-22 | DRIVE-THRU DELIGHTS SINGAPORE SG  |  -238.79 |\n"
        "| 2023-07-22 | FLAVORFUL MARKETPLAC SINGAPORE SG |    -2.71 |\n"
        "| 2023-07-23 | GOURMET PANTRY SINGAPORE SG       |     -8.5 |\n"
        "| 2023-07-23 | TRAVELER'S PROVISION SINGAPORE SG |      -59 |\n"
        "| 2023-07-23 | EPICUREAN CONNECT SINGAPORE SG    |     -3.2 |\n"
        "| 2023-07-23 | NATURAL BAZAAR SINGAPORE SG       |    -12.9 |\n"
        "| 2023-07-24 | WHOLESOME LIFE SINGAPORE SG       |   -27.75 |\n"
        "| 2023-07-24 | SAVORY MORNING SINGAPORE SG       |     -2.9 |\n"
        "| 2023-07-25 | METRO TRANSIT SINGAPORE SG        |   -17.16 |\n"
        "| 2023-07-25 | SUNNY CAFE SINGAPORE SG           |    -17.4 |\n"
        "| 2023-07-25 | GOLDEN TOAST SINGAPORE SG         |   -13.45 |\n"
        "| 2023-07-25 | -1234 SNOWY MART SINGAPORE SG     |    -1.45 |\n"
        "| 2023-07-25 | DRIVE EXPRESS SINGAPORE SG        |    -3.43 |\n"
        "| 2023-07-26 | GOURMET SHOP SINGAPORE SG         |     -7.3 |\n"
        "| 2023-07-26 | URBAN EATS SINGAPORE SG           |    -11.9 |\n"
        "| 2023-07-26 | FOOD HUB SINGAPORE SG             |     -6.5 |\n"
        "| 2023-07-26 | FRESH FINDS SINGAPORE SG          |    -2.44 |\n"
        "| 2023-07-26 | COZY CAFE SINGAPORE SG            |    -1.29 |\n"
        "| 2023-07-27 | PANTRY PICKS SINGAPORE SG         |    -17.9 |\n"
        "| 2023-07-27 | TRAVEL DELI SINGAPORE SG          |     -3.7 |\n"
        "| 2023-07-28 | GLOBAL GRUB SINGAPORE SG          |      -12 |\n"
        "| 2023-07-28 | FITNESS PASS SINGAPORE SG         |     -4.2 |\n"
        "| 2023-07-28 | NATURE FARE SINGAPORE SG          |    -3.04 |\n"
        "| 2023-07-29 | FAST FEAST SINGAPORE SG           |    -15.6 |\n"
        "| 2023-07-30 | QUICK MART SINGAPORE SG           |   -13.52 |\n"
        "| 2023-07-30 | CULINARY WAY SINGAPORE SG         |    -8.95 |\n"
        "| 2023-07-30 | COLD STORAGE SINGAPORE SG         |     -4.2 |\n"
        "| 2023-07-31 | BUS RIDE SINGAPORE SG             |    -11.9 |\n"
        "| 2023-07-31 | EATERY STOP SINGAPORE SG          |     -7.3 |\n"
        "| 2023-07-18 | CASH REBATE                       |     1.38 |\n"
        "+------------+-----------------------------------+----------+\n"
        "\n"
    )
    assert result.output == expected_output


def test_monopoly_no_pdf(cli_runner: CliRunner):
    with cli_runner.isolated_filesystem():
        with open("file.txt", "w") as f:
            f.write("not a pdf file")

        result = cli_runner.invoke(monopoly, ["file.txt"])

    assert result.exit_code == 1
    assert "Could not find .pdf files" in result.output


def test_get_statement_paths(test_directory: Path):
    path = test_directory
    expected = {
        path / "top_level.pdf",
        path / "top_level_2.pdf",
        path / "nested_directory/nested.pdf",
    }
    res = get_statement_paths(test_directory.iterdir())
    assert res == expected


def test_version_command(cli_runner: CliRunner):
    results = cli_runner.invoke(monopoly, args="--version")
    assert results.exit_code == 0
    assert results.stdout.startswith("monopoly, version ")
    semver_pattern = r"\d+\.\d+.\d+"
    match = re.search(semver_pattern, results.stdout)
    assert match, "Semantic version number not in output"


def test_pprint_transactions(capsys, statement):
    file = Path("test_file.md")

    transactions = [
        Transaction(transaction_date="2023-01-01", description="Transaction 1", amount=100.00),
        Transaction(transaction_date="2023-01-01", description="Transaction 2", amount=123.12),
    ]

    pprint_transactions(transactions, statement, file)

    captured = capsys.readouterr()

    expected_output = (
        "test_file.md\n"
        "+------------+---------------+----------+\n"
        "| date       | description   |   amount |\n"
        "|------------+---------------+----------|\n"
        "| 2023-01-01 | Transaction 1 |     -100 |\n"
        "| 2023-01-01 | Transaction 2 |  -123.12 |\n"
        "+------------+---------------+----------+\n"
        "\n"
    )
    assert captured.out == expected_output
