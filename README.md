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
| Citibank            | :white_check_mark:  | :x:                 |
| DBS                 | :white_check_mark:  | :white_check_mark:  |
| HSBC                | :white_check_mark:  | :x:                 |
| OCBC                | :white_check_mark:  | :white_check_mark:  |
| Standard Chartered  | :white_check_mark:  | :x:                 |

<h3 align="center">
    🎉 Monopoly is now live! 🎉
    <br><br>
    Try it out: <br>
    <a href="https://monopoly.streamlitapp.com/">https://monopoly.streamlitapp.com/</a>
</h3>

<p align="center">
    <img src="https://raw.githubusercontent.com/benjamin-awd/monopoly/main/docs/streamlit_demo.gif" width=800>
</p>

## Install
Clone the repo
```bash
git clone https://github.com/benjamin-awd/monopoly.git
```

Install dependencies using [Homebrew](https://brew.sh/)
```bash
brew install make
make setup
```

## Usage
Monopoly runs in your terminal, allowing you to extract, transform and write bank statements to a CSV file.

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
