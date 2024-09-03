from dataclasses import dataclass
from unittest.mock import PropertyMock, patch

from monopoly.banks.detector import BankDetector


@dataclass
class MockIdentifier1:
    pdf_version: float


@dataclass
class MockIdentifier2:
    title: str


@dataclass
class MockIdentifier3:
    foo: str


@dataclass
class TestBank:
    __test__ = False
    identifiers = [
        [
            MockIdentifier1(pdf_version=1.6),
            MockIdentifier2(title="Title"),
        ]
    ]


@patch.object(BankDetector, "metadata_items", new_callable=PropertyMock)
def test_is_bank_identified(mock_metadata_items, metadata_analyzer: BankDetector):
    """Test to check that all identifiers match on a bank"""
    # Test case 1: All identifiers match
    metadata_items = [
        MockIdentifier1(pdf_version=1.6),
        MockIdentifier2(title="Title"),
    ]
    mock_metadata_items.return_value = metadata_items
    assert metadata_analyzer.is_bank_identified(TestBank)

    # Test case 2: Only MockIdentifier1 matches
    metadata_items = [
        MockIdentifier1(pdf_version=1.6),
        MockIdentifier2(title="qwerty123"),
    ]
    mock_metadata_items.return_value = metadata_items
    assert not metadata_analyzer.is_bank_identified(TestBank)

    # Test case 3: Only MockIdentifier2 matches
    metadata_items = [
        MockIdentifier1(pdf_version=1.7),
        MockIdentifier2(title="Title"),
    ]
    mock_metadata_items.return_value = metadata_items
    assert not metadata_analyzer.is_bank_identified(TestBank)

    # Test case 4: No identifiers match
    metadata_items = [
        MockIdentifier1(pdf_version=1.7),
        MockIdentifier2(title="Different Title"),
    ]
    mock_metadata_items.return_value = metadata_items
    assert not metadata_analyzer.is_bank_identified(TestBank)

    # Test case 5: Partial match (missing identifier)
    metadata_items = [MockIdentifier1(pdf_version=1.6)]
    mock_metadata_items.return_value = metadata_items
    assert not metadata_analyzer.is_bank_identified(TestBank)
