# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
- Pretty-print mode with `--pprint` (no CSV output)
- OCR support with `--ocr` flag
- Safety check control with `--safe/--nosafe`

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
- Metadata for supported banks is stored in `src/monopoly/banks/<bank_name>/<bank_name>.py`
- Update the metadata comment header when adding new statement examples
