from dataclasses import dataclass
from unittest.mock import PropertyMock, patch

from monopoly.metadata import MetadataAnalyzer


@dataclass
class MockIdentifier1:
    key: str = ""
    value: str = ""


@dataclass
class MockIdentifier2:
    name: str = ""
    id: str = ""


@patch.object(MetadataAnalyzer, "metadata_items", new_callable=PropertyMock)
def test_pdf_properties_match_partial(
    mock_metadata_items, metadata_analyzer: MetadataAnalyzer
):
    metadata_items = [
        MockIdentifier1(key="test", value="123"),
        MockIdentifier2(name="doc", id="456"),
    ]
    mock_metadata_items.return_value = metadata_items

    grouped_identifiers = [
        MockIdentifier1(key="test", value="123"),
        MockIdentifier2(name="other", id="789"),
    ]

    assert not metadata_analyzer.pdf_properties_match(grouped_identifiers)


@patch.object(MetadataAnalyzer, "metadata_items", new_callable=PropertyMock)
def test_pdf_properties_match_type_mismatch(
    mock_metadata_items, metadata_analyzer: MetadataAnalyzer
):
    metadata_items = [MockIdentifier1(key="test", value="123")]
    mock_metadata_items.return_value = metadata_items

    grouped_identifiers = [MockIdentifier2(name="doc", id="456")]
    assert not metadata_analyzer.pdf_properties_match(grouped_identifiers)
