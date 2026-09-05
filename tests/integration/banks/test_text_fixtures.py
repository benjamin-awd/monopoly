"""Integration tests driven by community-contributed text fixtures.

These carry no real statement - just committed, redacted (or synthetic) page
text - so they run in every CI job with no encryption involved. Each fixture
lives in `tests/integration/text_fixtures/<bank>/<type>/` and contains:

    page_01.txt, page_02.txt, ...   redacted extracted page text
    metadata.json                   (optional) PDF metadata identifier fields
    raw.csv                         expected pre-transform transactions
    transformed.csv                 expected ISO-date transactions
    expected.json                   {bank, statement_type, total, statement_date}

Regenerate a fixture's CSVs from redacted text with `monopoly-fixture build`.
"""

import json
from pathlib import Path

import pytest
from test_utils.transactions import get_transactions_as_dict, read_pages, read_transactions_from_csv

from monopoly.banks import banks
from monopoly.generic import GenericBank
from monopoly.identifiers import MetadataIdentifier
from monopoly.pdf import PdfParser
from monopoly.pipeline import Pipeline

TEXT_FIXTURES_DIR = Path(__file__).parent.parent / "text_fixtures"


def _discover_fixtures() -> list[Path]:
    if not TEXT_FIXTURES_DIR.exists():
        return []
    return sorted(path.parent for path in TEXT_FIXTURES_DIR.glob("*/*/expected.json"))


def _bank_by_name(name: str):
    by_name = {bank.__name__: bank for bank in banks}
    by_name[GenericBank.__name__] = GenericBank
    return by_name[name]


FIXTURE_DIRS = _discover_fixtures()


@pytest.mark.parametrize(
    "fixture_dir",
    FIXTURE_DIRS,
    ids=[f"{path.parent.name}-{path.name}" for path in FIXTURE_DIRS],
)
def test_text_fixture(fixture_dir: Path):
    expected = json.loads((fixture_dir / "expected.json").read_text())
    bank = _bank_by_name(expected["bank"])

    pages = read_pages(fixture_dir)
    metadata = None
    metadata_path = fixture_dir / "metadata.json"
    if metadata_path.exists():
        metadata = MetadataIdentifier(**json.loads(metadata_path.read_text()))

    parser = PdfParser.from_pages(bank, pages, metadata=metadata, file_path=fixture_dir)
    pipeline = Pipeline(parser)
    statement = pipeline.extract()

    # raw transactions, captured before transform() mutates dates in place
    assert get_transactions_as_dict(statement.transactions) == read_transactions_from_csv(fixture_dir, "raw.csv")
    assert round(sum(tx.amount for tx in statement.transactions), 2) == expected["total"]
    assert statement.statement_date.isoformat() == expected["statement_date"]

    transformed = pipeline.transform(statement)
    assert get_transactions_as_dict(transformed) == read_transactions_from_csv(fixture_dir, "transformed.csv")
