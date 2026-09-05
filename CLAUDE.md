# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working in this repo

Scaffolding lives in `.claude/` (local only, gitignored). Prefer these over
improvising a workflow:

| Skill | Use for |
|---|---|
| `/plan` | Research a change and write a durable plan to `.claude/plans/` |
| `/execute` | Work a plan file, one verified step at a time |
| `/verify` | Run the full gate and report what passed, failed, or **skipped** |
| `/add-bank` | Add a bank or statement type from a sample PDF |
| `/debug-statement` | Diagnose a single PDF that fails to parse |

`dev-guide` (auto-loaded) is the reference for test/lint/type commands.
The `statement-debugger` subagent investigates a failing PDF without pulling
page dumps into the main context.

Two repo-specific rules that override normal instincts:

- **Real statements are PII.** `*.pdf` and `*.csv` are gitignored, and a
  PreToolUse hook blocks force-adding them. Never work around it. `.env` and
  `*.key` are denied to the Read tool by design. Your own statements live only
  in `Statements/` (gitignored) — never commit them.
- **Bank fixtures are synthetic.** Integration tests run against committed,
  hand-authored `page_NN.txt` text fixtures under
  `tests/integration/banks/<bank>/<type>/` (no encrypted PDFs, no encryption).
  They prove the parser handles each bank's *layout*, not that a specific real
  statement extracts correctly — so a regex change that breaks a real statement
  can still pass CI. Spot-check against a real file in `Statements/` with
  `uv run monopoly <file> --pprint` when changing extraction. Regenerate a
  fixture's CSVs from redacted text with `monopoly-fixture build` (see
  `CONTRIBUTING.md`).

## Project Overview

Monopoly is a Python library & CLI that converts bank statement PDFs to CSV. It parses bank statements using predefined configuration classes per bank, handles locked PDFs, supports OCR for image-based statements, and includes safety checks to validate transaction totals.

## Development Commands

### Setup
```bash
# Install dependencies (requires Homebrew on macOS)
brew install make
make setup
brew bundle

# Or using uv directly
uv venv
uv sync --all-extras
source .venv/bin/activate
```

### Testing
```bash
# Run all tests (default)
pytest .

# Run tests in parallel
pytest -n auto

# Run a single test file
pytest tests/unit/test_statement_date_filename_fallback.py

# Run a specific test
pytest tests/unit/test_statement_date_filename_fallback.py::test_name

# Run integration tests
pytest tests/integration/

# Run unit tests
pytest tests/unit/
```

### Code Quality
```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src

# Pre-commit hooks (runs ruff-check, ruff-format, pytest)
pre-commit run --all-files
```

### Building & Release
```bash
# Build package
uv build

# Release (runs git-cliff for changelog)
./release.sh
```

## Architecture

### Core Processing Pipeline

The ETL (Extract, Transform, Load) pipeline follows this flow:

1. **PDF Detection & Parsing** (`pdf.py`, `banks/detector.py`)
   - `PdfDocument` opens and unlocks PDFs (handles password-protected files)
   - `BankDetector` identifies the bank using identifier groups (metadata + text matching)
   - `PdfParser` extracts text from PDF pages using pdftotext, with optional OCR support

2. **Bank Configuration** (`banks/base.py`, `config.py`)
   - Each bank extends `BankBase` and defines:
     - `identifiers`: List of identifier groups (ANY group must match for detection)
     - `statement_configs`: List of `StatementConfig` for debit/credit statements
   - `StatementConfig` contains:
     - Regex patterns for transactions, statement dates, and headers
     - Date formats and parsing orders (DMY vs MDY)
     - Multiline configuration for descriptions spanning multiple lines
     - Safety check settings (validates totals)

3. **Statement Handling** (`handler.py`, `statements/`)
   - `StatementHandler` determines if statement is debit or credit by matching header patterns
   - `BaseStatement` (parent of `DebitStatement` and `CreditStatement`) extracts transactions:
     - Matches transaction patterns line-by-line
     - Handles multiline descriptions using `DescriptionExtractor`
     - Applies transaction bounds to filter out summary lines
     - Performs safety checks to validate transaction totals

4. **Pipeline Processing** (`pipeline.py`)
   - `Pipeline.extract()`: Extracts transactions and validates safety check
   - `Pipeline.transform()`: Converts dates to ISO 8601 with cross-year logic
   - `Pipeline.load()`: Writes transactions to CSV with generated or preserved filenames

### Bank Implementation Pattern

When adding a new bank, create a class in `src/monopoly/banks/<bank_name>/`:

```python
from monopoly.banks.base import BankBase
from monopoly.config import StatementConfig
from monopoly.identifiers import MetadataIdentifier, TextIdentifier


class NewBank(BankBase):
    name = "New Bank"

    # Define statement configs (debit/credit)
    credit = StatementConfig(
        statement_type=EntryType.CREDIT,
        transaction_pattern=re.compile(r"..."),
        statement_date_pattern=ISO8601.DD_MMM_YYYY,
        header_pattern=re.compile(r"..."),
        transaction_date_format="%d %b",
    )

    # Identifier groups: ANY group must fully match
    identifiers = [
        [TextIdentifier("Bank Name"), MetadataIdentifier(creator="Producer")],
        [TextIdentifier("Bank Name"), MetadataIdentifier(producer="Other Producer")],
    ]

    statement_configs = [credit, debit]
```

### Key Concepts

- **Identifier Groups**: A bank is detected if ANY identifier group has ALL identifiers matching. Empty groups are ignored.
- **Transaction Patterns**: Named capture groups must include `transaction_date`, `description`, and `amount`.
- **Multiline Descriptions**: Enabled via `MultilineConfig` to concatenate descriptions split across lines.
- **Transaction Bounds**: Filter out summary/balance lines by setting a character position limit.
- **Safety Check**: Validates that sum of transactions matches the total in the statement (enabled by default).
- **Cross-Year Logic**: Handles transactions from previous year when statement date is in Jan/Feb.

### Testing

- **Integration tests** (`tests/integration/`): Test complete pipeline with real bank statements
- **Unit tests** (`tests/unit/`): Test individual components (e.g., multiline descriptions, date parsing)
- Test utilities in `tests/test_utils/` provide fixtures and helpers

### CLI Entry Point

The CLI (`src/monopoly/cli/cli.py`) supports:
- Single file or directory processing
- Parallel processing using `ProcessPoolExecutor`
- Output directory specification with `--output`
- Filename preservation with `--preserve-filename`
- Output format with `--format csv|json` (`-f`). CSV stays a fixed 4-column
  contract; JSON emits the versioned richer schema built by
  `src/monopoly/serialize.py` (`SCHEMA_VERSION`, statement metadata, payment
  summary, top-level `balances`, and a unique per-transaction `id`).
  `SCHEMA_VERSION` is a single integer that bumps **only on a breaking change**
  (removing/renaming a field, changing a value's type/meaning/units, or
  restructuring nesting — e.g. v2 moved balance rows out of `transactions`).
  Adding a new **optional/nullable** field is NOT breaking and must NOT bump it;
  consumers are expected to ignore fields they don't recognize (tolerant reader).
- Pretty-print mode with `--pprint` (no CSV output)
- OCR support with `--ocr` flag
- Safety check control with `--safe/--nosafe`

The JSON schema carries `currency` (per-`StatementConfig` settlement currency),
`posting_date`, a normalized `direction` (`"credit"`/`"debit"`, replacing the old
raw `polarity` marker), and a nullable `account` slot. `Transaction.direction` is
normalized in the model; the internal parser still captures raw markers into
`RawTransaction.direction`. Known follow-ups (currently `None`): per-transaction
original/FX currency + amount, account last-4, and `period_start`.

A previous-balance row is not a transaction, so it goes in a separate top-level
`balances` list (`{type, amount, date, direction, currency}`) rather than in
`transactions`. `type` is `"previous"` today (`"opening"`/`"closing"` may come
later). Internally the row is marked with `Transaction.kind` and kept in the
transaction list so the safety-check total still adds up; only `serialize.py`
moves it into `balances` for output. `kind` stays internal — it is never written
to the CSV or the filename/id hashes.

This v1→v2 change is a breaking one: the balance row moved out of `transactions`,
so an old reader that lists or sums transactions would silently miss it. That is
why `SCHEMA_VERSION` was bumped. Consumers should check `schema_version` and
refuse anything newer than they understand.

Per-transaction `id`: the JSON `"id"` is *unique within an envelope* and is the
only sanctioned per-row identifier, produced by `serialize.assign_ids`. It is a
transaction's `Transaction.content_hash` for the first occurrence of a given
fingerprint and a re-hash of `(content_hash, n)` for the nth duplicate — so two
genuinely-distinct transactions with identical fields (e.g. two identical
same-day transfers) still get distinct ids. `content_hash` itself is a *content
fingerprint that deliberately collides* for identical content; never use it
directly as a per-row id (that reintroduces collisions). Two caveats: (1) the
occurrence ordinal is stable within one statement's row order but cannot
guarantee cross-statement stability if a bank re-sorts identical same-day rows
in an overlapping statement — inherent to a stateless parser; (2) populating the
`account` follow-up (issue #308) folds a new field into `content_hash` and will
rotate *every* `id`, not just duplicates.

## Important Implementation Notes

### Password-Protected PDFs
- Passwords are loaded from `.env` file or `PDF_PASSWORDS` environment variable
- Format: `PDF_PASSWORDS=["password1","password2"]`
- The system tries each password until one works

### OCR Support
- OCR is applied when `--ocr` flag is used or when `ocr_identifiers` match
- Requires `ocrmypdf` package (installed with `[ocr]` extra)
- OCR configuration in `tesseract.cfg`

### Date Parsing
- Primary: Extract from PDF content using `statement_date_pattern`
- Fallback: Extract from filename using `filename_fallback_pattern` (if configured)
- Cross-year detection handles statements from Jan/Feb with Dec transactions

### Adding Statement Metadata
- Metadata identifiers for supported banks live in `src/monopoly/banks/<bank_name>/<bank_name>.py`
- Producer/creator strings vary by statement vintage. When a new example does not
  match, add another identifier group rather than loosening an existing one, and
  comment what vintage it covers (see `hsbc.py` for the pattern)
