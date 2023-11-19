![](https://raw.githubusercontent.com/benjamin-awd/monopoly/main/docs/logo.svg)

-----------------

[![Tests](https://github.com/benjamin-awd/monopoly/workflows/tests/badge.svg)](https://github.com/benjamin-awd/monopoly/actions)
[![CI](https://github.com/benjamin-awd/monopoly/workflows/ci/badge.svg)](https://github.com/benjamin-awd/monopoly/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: pylint](https://img.shields.io/badge/linting-pylint-orange)](https://github.com/pylint-dev/pylint)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


Monopoly is a Python library that converts Singapore bank statement PDFs to CSV using pdftotext

Supported banks:
- Citibank
- DBS
- HSBC
- OCBC
- Standard Chartered

Only credit card statements are supported (for now)

## Install
Clone the repo
```bash
git clone https://github.com/benjamin-awd/monopoly.git
```

Install dependencies using [Homebrew](https://brew.sh/)
```bash
brew bundle
```

Create a virtual environment and install Python dependencies
```bash
pyenv virtualenv 3.11.4 monopoly
pyenv shell monopoly
poetry install
```

## Usage
Monopoly can be run as a Python package, allowing you to extract, transform and write bank statements to a CSV file.

To see how Monopoly works, you can run this [example](monopoly/examples/single_statement.py)
```bash
python3 monopoly/examples/single_statement.py
```

If your PDF is encrypted, you'll have to add the password to a .env file in the root directory, which is automatically read by monopoly

You can use the .env.template and then update values in the .env file
```
cp .env.template .env
```

## Features
- Support for encrypted PDFs -- passwords can be passed in via a .env file, or passed directly via a bank class
- PDFs can also be unlocked with a static string, and a masking pattern like ?d?d?d for banks like HSBC that use a common password prefix (DOB), but different passwords for each card
- Cashback transactions from Citibank and OCBC are also supported, and appear as "negative" transactions
- Monopoly can be run on Google Cloud as a scheduled Cloud Run job, which opens up more sophisticated use-cases like historical analysis and personal finance visualization
