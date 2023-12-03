import os
import subprocess
from pathlib import Path
from typing import Type
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from monopoly.cli import (
    Report,
    Result,
    get_statement_paths,
    monopoly,
    process_statement,
)
from monopoly.processors import ProcessorBase


@pytest.fixture
def mock_results():
    result1 = Result(
        source_file_name="statement1.pdf", target_file_name="processed1.csv"
    )
    result2 = Result(source_file_name="statement2.pdf", error_info={"message": "Error"})
    return [result1, result2]


@pytest.fixture
def test_directory() -> Path:
    return Path("tests/unit/test_cli").resolve()


def test_display_report(mock_results, capsys):
    # Create a Report object with mock results
    report = Report(results=mock_results)

    # Call the display_report method
    report.display_report()

    # Capture and check the printed output
    captured = capsys.readouterr()
    printed_output = captured.out.strip().split("\n")

    # Check assertions based on the mock results
    assert "1 statement(s) had errors while processing" in printed_output
    assert "1 statement(s) processed" in printed_output
    assert "statement1.pdf -> processed1.csv" in printed_output
    assert "statement2.pdf -- Error" in printed_output


def run_cli_command(commands: list[str]) -> subprocess.CompletedProcess:
    process = subprocess.run(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
    )
    return process


def test_help_command() -> None:
    cli_runner = CliRunner(mix_stderr=False)
    help_results = cli_runner.invoke(monopoly, args="--help")
    assert help_results.exit_code == 0
    assert help_results.stdout.startswith("Usage: monopoly")


def test_process_statement(monkeypatch):
    processor: ProcessorBase | Type[Mock] = Mock(spec=ProcessorBase)

    def mock_detect_processor(file_path: Path) -> Mock:
        assert "statement.pdf" in str(file_path)
        processor.load.return_value = Path("foo")
        return processor

    monkeypatch.setattr("monopoly.cli.detect_processor", mock_detect_processor)

    file = Path("path/to/statement.pdf")

    process_statement(file, "foo", False)

    processor.extract.assert_called_once()
    processor.transform.assert_called_once()
    processor.load.assert_called_once()


def test_monopoly_output():
    cli_runner = CliRunner()
    with open("tests/integration/banks/citibank/credit/input.pdf", "rb") as source_file:
        file_content = source_file.read()

    with cli_runner.isolated_filesystem() as tmp_dir:
        with open(f"{tmp_dir}/input.pdf", "wb") as destination_file:
            destination_file.write(file_content)

        result_dir = "results"
        os.mkdir(result_dir)
        result = cli_runner.invoke(
            monopoly, [".", "--output", f"{tmp_dir}/{result_dir}"]
        )

        assert result.exit_code == 0
        assert "1 statement(s) processed" in result.output
        assert "input.pdf -> citibank-credit-2022-11-e47be3.csv" in result.output


def test_monopoly_no_pdf():
    cli_runner = CliRunner()

    with cli_runner.isolated_filesystem():
        with open("file.txt", "w") as f:
            f.write("not a pdf file")

        result = cli_runner.invoke(monopoly, ["file.txt"])

    assert result.exit_code == 1
    assert "Could not find .pdf files" in result.output


def test_get_statement_paths(test_directory: Path) -> None:
    path = test_directory
    expected = {
        path / "top_level.pdf",
        path / "top_level_2.pdf",
        path / "nested_directory/nested.pdf",
    }
    res = get_statement_paths(test_directory.iterdir())
    assert res == expected
