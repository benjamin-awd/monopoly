from dataclasses import dataclass

from monopoly.banks import all_identifiers_match


@dataclass
class MockIdentifier1:
    key: str = ""
    value: str = ""


@dataclass
class MockIdentifier2:
    name: str = ""
    id: str = ""


def test_all_identifiers_match_partial():
    metadata_items = [
        MockIdentifier1(key="test", value="123"),
        MockIdentifier2(name="doc", id="456"),
    ]

    grouped_identifiers = [
        MockIdentifier1(key="test", value="123"),
        MockIdentifier2(name="other", id="789"),
    ]

    assert not all_identifiers_match(metadata_items, grouped_identifiers)


def test_all_identifiers_match_type_mismatch():
    metadata_items = [MockIdentifier1(key="test", value="123")]
    grouped_identifiers = [MockIdentifier2(name="doc", id="456")]
    assert not all_identifiers_match(metadata_items, grouped_identifiers)
