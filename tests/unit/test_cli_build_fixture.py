"""Unit tests for `monopoly-fixture build`.

Builds CSV fixtures from hand-written (redacted-style) page text, with no PDF.
ExampleBank is not in the registry by default, so it's monkeypatched in.
"""

import csv
import json

import pytest
from click.testing import CliRunner

from monopoly.cli.fixtures import fixtures
from monopoly.examples.example_bank import ExampleBank

# ExampleBank credit config: statement date, header, two transactions, and a
# printed total (12.34 + 56.78 = 69.12) so the safety check passes.
GOOD_PAGE = "01-02-2024\nDATE DESCRIPTION AMOUNT\n12/01 COFFEE SHOP 12.34\n13/01 BOOK STORE 56.78\nTOTAL 69.12\n"

# Same printed total, but an edited amount makes the sum (72.34) absent from the
# document - the kind of mistake a careless redaction introduces.
BROKEN_PAGE = "01-02-2024\nDATE DESCRIPTION AMOUNT\n12/01 COFFEE SHOP 12.34\n13/01 BOOK STORE 60.00\nTOTAL 69.12\n"


@pytest.fixture
def _register_example_bank(monkeypatch):
    monkeypatch.setattr("monopoly.cli.fixtures.banks", [ExampleBank])


def _write_fixture_dir(directory, page_text):
    (directory / "page_01.txt").write_text(page_text, encoding="utf8")


def test_build_writes_three_fixture_files(tmp_path, _register_example_bank):
    _write_fixture_dir(tmp_path, GOOD_PAGE)

    result = CliRunner().invoke(fixtures, ["build", str(tmp_path), "--bank", "ExampleBank"])
    assert result.exit_code == 0, result.output

    with (tmp_path / "raw.csv").open() as file:
        raw_rows = list(csv.DictReader(file))
    assert [row["description"] for row in raw_rows] == ["COFFEE SHOP", "BOOK STORE"]

    with (tmp_path / "transformed.csv").open() as file:
        transformed_rows = list(csv.DictReader(file))
    assert [row["date"] for row in transformed_rows] == ["2024-01-12", "2024-01-13"]

    expected = json.loads((tmp_path / "expected.json").read_text())
    assert expected["bank"] == "ExampleBank"
    assert expected["statement_type"] == "credit"
    assert abs(expected["total"]) == 69.12
    assert expected["statement_date"].startswith("2024-02-01")


def test_build_safety_check_catches_broken_total(tmp_path, _register_example_bank):
    _write_fixture_dir(tmp_path, BROKEN_PAGE)

    result = CliRunner().invoke(fixtures, ["build", str(tmp_path), "--bank", "ExampleBank"])
    assert result.exit_code != 0
    assert not (tmp_path / "raw.csv").exists()


def test_build_nosafe_skips_safety_check(tmp_path, _register_example_bank):
    _write_fixture_dir(tmp_path, BROKEN_PAGE)

    result = CliRunner().invoke(fixtures, ["build", str(tmp_path), "--bank", "ExampleBank", "--nosafe"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "raw.csv").exists()


def test_build_requires_bank_or_generic(tmp_path, _register_example_bank):
    _write_fixture_dir(tmp_path, GOOD_PAGE)

    result = CliRunner().invoke(fixtures, ["build", str(tmp_path)])
    assert result.exit_code != 0
    assert "Pass --bank NAME or --generic" in result.output
