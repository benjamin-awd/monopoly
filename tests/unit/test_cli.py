import os
import re
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from monopoly.cli import (
    Report,
    Result,
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
    return Path("tests/unit/test_cli").resolve()


@pytest.fixture
def cli_runner():
    yield CliRunner()


def run_cli_command(commands: list[str]) -> subprocess.CompletedProcess:
    process = subprocess.run(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
    )
    return process


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
