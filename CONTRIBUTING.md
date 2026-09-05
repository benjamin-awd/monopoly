# Contributing

## Add a bank without sharing a statement

Every bank is tested against a **text fixture**: the extracted, redacted (or
synthetic) page text of a statement, checked in as plain `page_NN.txt` files.
The repo commits no real statements and uses no encryption — a real statement
is PII, so it never leaves your machine. Fixtures live under
`tests/integration/banks/<bank>/<type>/` (maintainer set, full assertions) and
`tests/integration/text_fixtures/<bank>/<type>/` (community-contributed); both
run in every CI job.

The `monopoly-fixture` command builds one for you, using the *real* parser so
the fixture text matches exactly what extraction sees (cropbox, vertical-text
removal, `pdftotext` layout).

### 1. Dump the page text

```bash
monopoly-fixture dump path/to/statement.pdf -o tests/integration/text_fixtures/<bank>/<type>
```

This detects the bank (or pass `--bank <ClassName>` / `--generic`) and writes
one `page_NN.txt` per page plus a `metadata.json`.

### 2. Redact the page files

Edit each `page_NN.txt` and remove anything that identifies a real person or
their spending — cardholder name, account/card numbers, address, and the
transaction descriptions (merchant names).

**Keep every date and amount exactly as-is.** They drive the safety check; if
you change a number the fixture will no longer validate. Redact descriptions to
stable placeholders (e.g. `MERCHANT 1`) — consistency doesn't matter across the
CSVs because the next step regenerates them from the redacted text.

### 3. Build the CSV fixtures

```bash
monopoly-fixture build tests/integration/text_fixtures/<bank>/<type> --bank <ClassName>
```

This parses the **redacted** text through the real pipeline, re-runs the safety
check (so a redaction that broke a total fails here, not in CI), and writes
`raw.csv`, `transformed.csv`, and `expected.json`. Because the CSVs are derived
from the redacted text, they cannot disagree with it.

If the statement genuinely has no total to check against, use `--nosafe`.

### 4. Verify and submit

```bash
pytest tests/integration/banks/test_text_fixtures.py -k <bank>
```

Confirm your case is collected and passes (not `0 selected`). Then open a PR
with the `tests/integration/text_fixtures/<bank>/<type>/` directory. Do **not**
commit the original PDF.

> A text fixture exercises extraction and transformation, but not bank
> *detection* (the bank is selected explicitly, not sniffed from PDF metadata).
> Detection is covered separately via the unencrypted `example_statement.pdf`.
