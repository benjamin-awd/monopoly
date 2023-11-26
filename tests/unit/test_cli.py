import os
import subprocess
from pathlib import Path
from unittest.mock import DEFAULT, MagicMock, patch

import pytest
from click.testing import CliRunner

from monopoly.cli import get_statement_paths, monopoly, run


@pytest.fixture
def test_directory() -> Path:
    return Path("tests/unit/test_cli").resolve()


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


class MockBank(MagicMock):
    def extract(self):
        pass

    def transform(self):
        pass

    def load(self):
        pass


def test_run(monkeypatch):
    def mock_auto_detect_bank(file_path: Path):
        assert "statement.pdf" in str(file_path)
        return MockBank()

    monkeypatch.setattr("monopoly.cli.auto_detect_bank", mock_auto_detect_bank)

    # Mock paths
    files = [Path("path/to/statement.pdf").resolve()]

    with patch.multiple(MockBank, extract=DEFAULT, transform=DEFAULT, load=DEFAULT):
        run(files)

        assert isinstance(MockBank.extract, MagicMock)
        assert isinstance(MockBank.transform, MagicMock)
        assert isinstance(MockBank.load, MagicMock)

        # Assertions
        MockBank.extract.assert_called_once()
        MockBank.transform.assert_called_once()
        MockBank.load.assert_called_once()


def test_monopoly_output():
    cli_runner = CliRunner()
    with open("tests/integration/banks/citibank/input.pdf", "rb") as source_file:
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
        assert "input.pdf -> citibank-credit-2022-11.csv" in result.output


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
