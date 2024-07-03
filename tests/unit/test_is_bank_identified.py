from dataclasses import dataclass

from monopoly.banks import is_bank_identified


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


def test_is_bank_identified():
    """Test to check that all identifiers match on a bank"""
    # Test case 1: All identifiers match
    metadata_items = [
        MockIdentifier1(pdf_version=1.6),
        MockIdentifier2(title="Title"),
    ]
    assert is_bank_identified(metadata_items, TestBank)

    # Test case 2: Only MockIdentifier1 matches
    metadata_items = [
        MockIdentifier1(pdf_version=1.6),
        MockIdentifier2(title="qwerty123"),
    ]
    assert not is_bank_identified(metadata_items, TestBank)

    # Test case 3: Only MockIdentifier2 matches
    metadata_items = [
        MockIdentifier1(pdf_version=1.7),
        MockIdentifier2(title="Title"),
    ]
    assert not is_bank_identified(metadata_items, TestBank)

    # Test case 4: No identifiers match
    metadata_items = [
        MockIdentifier1(pdf_version=1.7),
        MockIdentifier2(title="Different Title"),
    ]
    assert not is_bank_identified(metadata_items, TestBank)

    # Test case 5: Partial match (missing identifier)
    metadata_items = [MockIdentifier1(pdf_version=1.6)]
    assert not is_bank_identified(metadata_items, TestBank)
