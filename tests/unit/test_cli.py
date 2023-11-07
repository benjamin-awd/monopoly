from pathlib import Path
from unittest.mock import DEFAULT, MagicMock, patch

import pytest

from monopoly.cli import get_statement_paths, run


@pytest.fixture
def test_directory() -> Path:
    return Path("tests/unit/test_cli").resolve()


class MockBank(MagicMock):
    def extract(self):
        pass

    def transform(self):
        pass

    def load(self):
        pass


def test_run(monkeypatch):
    def mock_auto_detect_bank(file_path: Path):
        assert "input.pdf" in str(file_path)
        return MockBank()

    monkeypatch.setattr("monopoly.cli.auto_detect_bank", mock_auto_detect_bank)

    # Mock paths
    files = [Path("tests/integration/banks/example/input.pdf").resolve()]

    with patch.multiple(MockBank, extract=DEFAULT, transform=DEFAULT, load=DEFAULT):
        run(files)

        assert isinstance(MockBank.extract, MagicMock)
        assert isinstance(MockBank.transform, MagicMock)
        assert isinstance(MockBank.load, MagicMock)

        # Assertions
        MockBank.extract.assert_called_once()
        MockBank.transform.assert_called_once()
        MockBank.load.assert_called_once()


def test_get_statement_paths(test_directory: Path) -> None:
    path = test_directory
    expected = {
        path / "top_level.pdf",
        path / "top_level_2.pdf",
        path / "nested_directory/nested.pdf",
    }
    res = get_statement_paths(test_directory.iterdir())
    assert res == expected
