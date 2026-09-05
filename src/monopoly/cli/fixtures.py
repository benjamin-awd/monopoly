"""
CLI for building shareable, redactable text fixtures from PDF statements.

Exposed as the ``monopoly-fixture`` command. Contributors can add a bank
without handing over a real statement: ``dump`` extracts page text through the
*real* parser (so it matches what extraction sees) into per-page ``page_NN.txt``
files they redact, and ``build`` regenerates the CSV fixtures from that redacted
text (so the CSVs cannot drift from it) and re-runs the safety check.
"""

import csv
import json
from dataclasses import asdict
from pathlib import Path

import click
import pymupdf

from monopoly.banks import BankDetector, banks
from monopoly.banks.base import BankBase
from monopoly.generic import GenericBank
from monopoly.identifiers import MetadataIdentifier
from monopoly.pdf import PdfDocument, PdfParser
from monopoly.pipeline import Pipeline


def _page_filename(index: int, total: int) -> str:
    """Zero-padded per-page filename, e.g. page_01.txt (lexically sortable)."""
    width = max(2, len(str(total)))
    return f"page_{index:0{width}d}.txt"


def _resolve_bank(
    *,
    bank_name: str | None,
    generic: bool,
    document: PdfDocument | None = None,
) -> type[BankBase]:
    """Pick the bank: explicit --bank, --generic, or (with a document) auto-detection."""
    if generic:
        return GenericBank
    if bank_name:
        by_name = {bank.__name__: bank for bank in banks}
        if bank_name not in by_name:
            available = ", ".join(sorted(by_name))
            msg = f"Unknown bank {bank_name!r}. Available: {available}"
            raise click.ClickException(msg)
        return by_name[bank_name]
    if document is not None:
        bank = BankDetector(document).detect_bank(banks)
        if bank is not None:
            return bank
    msg = "Could not determine bank. Pass --bank NAME or --generic."
    raise click.ClickException(msg)


def _read_pages(directory: Path) -> list[str]:
    """Read redacted page_*.txt files from a fixture directory, in page order."""
    page_files = sorted(directory.glob("page_*.txt"))
    if not page_files:
        msg = f"No page_*.txt files found in {directory}"
        raise click.ClickException(msg)
    return [path.read_text(encoding="utf8") for path in page_files]


# Fixed-pitch (Courier) grid used by `render`. Courier is a monospace Base-14
# font whose glyph advance is ~0.6 * fontsize, so every character - including
# leading spaces - occupies one fixed-width cell. Laying each page_NN.txt line
# out on this grid lets `pdftotext --physical` reconstruct the exact columns the
# bank regexes (and debit withdrawal/deposit classification) depend on.
_RENDER_FONT = "courier"
_RENDER_FONT_SIZE = 10.0
_RENDER_CHAR_WIDTH = _RENDER_FONT_SIZE * 0.6
_RENDER_LINE_HEIGHT = _RENDER_FONT_SIZE * 1.5
_RENDER_MARGIN = 20.0


def _render_pages_to_pdf(pages: list[str]) -> pymupdf.Document:
    """Render page text onto a fixed-pitch Courier grid, one PDF page per text page."""
    document = pymupdf.open()
    for text in pages:
        lines = text.split("\n")
        columns = max((len(line) for line in lines), default=1)
        width = 2 * _RENDER_MARGIN + max(columns, 1) * _RENDER_CHAR_WIDTH
        height = 2 * _RENDER_MARGIN + max(len(lines), 1) * _RENDER_LINE_HEIGHT
        page = document.new_page(width=width, height=height)
        for row, line in enumerate(lines):
            if not line:
                continue
            baseline = _RENDER_MARGIN + (row + 1) * _RENDER_LINE_HEIGHT
            page.insert_text(
                (_RENDER_MARGIN, baseline),
                line,
                fontname=_RENDER_FONT,
                fontsize=_RENDER_FONT_SIZE,
            )
    return document


def _read_metadata(directory: Path) -> MetadataIdentifier | None:
    metadata_path = directory / "metadata.json"
    if not metadata_path.exists():
        return None
    return MetadataIdentifier(**json.loads(metadata_path.read_text(encoding="utf8")))


def _write_csv(path: Path, transactions: "list") -> None:
    """Write transactions as the 3-column raw form the integration tests read."""
    rows = [tx.as_raw_dict() for tx in transactions]
    fieldnames = list(rows[0].keys()) if rows else ["date", "description", "amount"]
    with path.open("w", encoding="utf8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@click.group()
def fixtures() -> None:
    """Build shareable text fixtures from PDF statements."""


@fixtures.command()
@click.argument(
    "file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    "output_directory",
    type=click.Path(file_okay=False, resolve_path=True, path_type=Path),
    default=None,
    help="Directory for pages.txt/metadata.json (defaults to the PDF's directory).",
)
@click.option("--bank", "bank_name", default=None, help="Force a bank by class name instead of auto-detecting.")
@click.option("--generic", is_flag=True, help="Use the generic handler instead of detecting a bank.")
def dump(file: Path, output_directory: Path | None, bank_name: str | None, generic: bool) -> None:  # noqa: FBT001
    """
    Extract redactable page text from a PDF into a text fixture.

    Runs the real parser (cropbox, vertical-text removal, pdftotext) so the text
    matches what extraction sees, then writes one page_NN.txt per page plus
    metadata.json. No CSV is produced. Redact PII in the page files before
    sharing, then run `monopoly-fixture build` on the redacted directory.
    """
    document = PdfDocument(file)
    document.unlock_document()

    bank = _resolve_bank(bank_name=bank_name, generic=generic, document=document)
    parser = PdfParser(bank, document)
    pages = parser.pages

    output_directory = output_directory or file.parent
    output_directory.mkdir(parents=True, exist_ok=True)

    total = len(pages)
    for index, page in enumerate(pages, start=1):
        (output_directory / _page_filename(index, total)).write_text(page.raw_text, encoding="utf8")
    metadata_path = output_directory / "metadata.json"
    metadata_path.write_text(json.dumps(asdict(parser.metadata_identifier), indent=2), encoding="utf8")

    click.secho(f"Detected bank: {bank.__name__}", fg="green")
    click.secho(f"Wrote {total} page file(s) + metadata.json to {output_directory}", fg="green")
    click.secho(
        "Redact PII in the page_*.txt files before sharing - keep dates and amounts intact.",
        fg="yellow",
        bold=True,
    )


@fixtures.command()
@click.argument(
    "directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path),
)
@click.option("--bank", "bank_name", default=None, help="Bank class name (required unless --generic).")
@click.option("--generic", is_flag=True, help="Use the generic handler instead of a specific bank.")
@click.option(
    "--safe/--nosafe",
    "safety_check",
    default=True,
    help="Re-run the safety check on the redacted text (default: on).",
)
def build(directory: Path, bank_name: str | None, generic: bool, safety_check: bool) -> None:  # noqa: FBT001
    """
    Build CSV fixtures from redacted page_*.txt files.

    Parses the redacted text through the real pipeline, re-runs the safety check
    (so redaction that broke a total fails here, not in CI), and writes raw.csv,
    transformed.csv and expected.json into DIRECTORY. Because the CSVs are
    derived from the redacted text, they cannot disagree with it.
    """
    bank = _resolve_bank(bank_name=bank_name, generic=generic)
    pages = _read_pages(directory)
    metadata = _read_metadata(directory)

    parser = PdfParser.from_pages(bank, pages, metadata=metadata, file_path=directory)
    pipeline = Pipeline(parser)
    statement = pipeline.extract(safety_check=safety_check)

    # capture raw rows before transform(), which mutates transaction dates in place
    _write_csv(directory / "raw.csv", statement.transactions)
    total = round(sum(tx.amount for tx in statement.transactions), 2)

    transformed = pipeline.transform(statement)
    _write_csv(directory / "transformed.csv", transformed)

    expected = {
        "bank": bank.__name__,
        "statement_type": str(statement.statement_type),
        "total": total,
        "statement_date": statement.statement_date.isoformat(),
    }
    (directory / "expected.json").write_text(json.dumps(expected, indent=2), encoding="utf8")

    click.secho(f"Extracted {len(statement.transactions)} transaction(s); total {total}", fg="green")
    click.secho(f"Wrote raw.csv, transformed.csv, expected.json to {directory}", fg="green")


@fixtures.command()
@click.argument(
    "directory",
    type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, resolve_path=True, path_type=Path),
    default=None,
    help="Destination PDF path (defaults to <directory>/rendered.pdf).",
)
def render(directory: Path, output_path: Path | None) -> None:
    """
    Render redacted page_*.txt files back into a synthetic PDF.

    Each page is laid out on a fixed-pitch Courier grid so that
    `pdftotext --physical` reconstructs the same columns the real pipeline
    parses. The result carries no real-statement PII (it is built from the
    committed text) and is used to benchmark `monopoly` end-to-end without
    committing binary PDFs. This is the inverse of `dump` (PDF -> text).
    """
    pages = _read_pages(directory)
    output_path = output_path or directory / "rendered.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    document = _render_pages_to_pdf(pages)
    document.save(str(output_path))
    document.close()

    click.secho(f"Rendered {len(pages)} page(s) to {output_path}", fg="green")
