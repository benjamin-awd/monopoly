![](https://raw.githubusercontent.com/benjamin-awd/monopoly/main/docs/logo.svg)

-----------------
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://monopoly.streamlit.app)
[![Tests](https://github.com/benjamin-awd/monopoly/actions/workflows/tests.yaml/badge.svg?branch=main&event=push)](https://github.com/benjamin-awd/monopoly/actions/workflows/tests.yaml)
[![CI](https://github.com/benjamin-awd/monopoly/actions/workflows/ci.yaml/badge.svg?branch=main&event=push)](https://github.com/benjamin-awd/monopoly/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Monopoly is a Python library & CLI that converts Singapore bank statement PDFs to CSV.

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
Monopoly can be run as a Python package, allowing you to extract, transform and write bank statements to a CSV file.

To see how Monopoly works, you can run this example
```bash
python3 src/monopoly/examples/single_statement.py
```

If you need to run monopoly on a password protected file, ensure that passwords are set in the .env file:
```sh
cp .env.template env
```

If you have multiple statements from the same bank with different passwords (e.g. HSBC statements), make sure to set both passwords in an array format like so:
```sh
HSBC_PDF_PASSWORDS=["password1","password2"]
```

## Features
- Unlocks PDFs using user-provided credentials
- Statements can be parsed with the CLI, or manually with the bank processor class.
- Support for cashback transactions and refunds
- Monopoly can be run on Google Cloud as a scheduled Cloud Run job, which opens up more sophisticated use-cases like historical analysis and personal finance visualization
