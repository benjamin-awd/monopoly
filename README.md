![](https://raw.githubusercontent.com/benjamin-awd/monopoly/main/docs/logo.svg)

-----------------
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://monopoly.streamlit.app)
[![Tests](https://github.com/benjamin-awd/monopoly/actions/workflows/tests.yaml/badge.svg?branch=main&event=push)](https://github.com/benjamin-awd/monopoly/actions/workflows/tests.yaml)
[![CI](https://github.com/benjamin-awd/monopoly/actions/workflows/ci.yaml/badge.svg?branch=main&event=push)](https://github.com/benjamin-awd/monopoly/actions/workflows/ci.yaml)
[![License: AGPL 3.0](https://img.shields.io/badge/License-AGPL%203.0-blue)](https://opensource.org/license/agpl-v3)

Monopoly is a Python library & CLI that converts bank statement PDFs to CSV.

![](https://raw.githubusercontent.com/benjamin-awd/monopoly/main/docs/monopoly.gif)

Supported banks:
| Bank                | Credit Statement    | Debit Statement     |
| --------------------| --------------------| --------------------|
| Citibank            | ✅                 | ❌                  |
| DBS/POSB            | ✅                 | ✅                  |
| HSBC                | ✅                 | ❌                  |
| Maybank             | ✅                 | ✅                  |
| OCBC                | ✅                 | ✅                  |
| Standard Chartered  | ✅                 | ❌                  |

## Install
Monopoly is a pip-installable Python package on [PyPI](https://pypi.org/project/monopoly-core) under the name `monopoly-core`.

Since Monopoly uses `pdftotext`, you'll need to install additional dependencies:

```sh
apt-get install build-essential libpoppler-cpp-dev pkg-config
```

Then intall with pipx:
```sh
pipx install monopoly-core
```

## Usage
Monopoly runs in your terminal, allowing you to extract, transform and write bank statements to a CSV file.

To list commands and options:
```sh
monopoly --help
```

You can run it on a single statement
```sh
monopoly src/monopoly/examples/example_statement.pdf
```

or multiple statements
```sh
monopoly ./statements
```

If you need to run monopoly on a password protected file, ensure that passwords are set in the .env file:
```sh
cp .env.template env
```

If you have multiple statements from the same bank with different passwords, make sure to set both passwords in an array format:
```sh
HSBC_PDF_PASSWORDS=["password1","password2"]
```

Monopoly can also be run as a Python [library](src/monopoly/examples/single_statement.py):
```bash
python3 src/monopoly/examples/single_statement.py
```

## Features
- Parses PDFs using predefined configuration classes per bank.
- Handles locked PDFs with credentials passed via environment variables.
- Supports a variety of date/number formats and determines if a transaction is debit or credit.
- Provides a generic parser that can be used without any predefined configuration (caveat emptor).
- Includes a safety check (enabled by default) that validates totals for debit or credit statements.

## Development

Clone the repo
```bash
git clone https://github.com/benjamin-awd/monopoly.git
```

Install dependencies using [Homebrew](https://brew.sh/)
```bash
brew install make
make setup
brew bundle --file Brewfile.dev
```
