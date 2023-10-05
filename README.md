# Monopoly
Monopoly is a Python library that extracts transactions from bank statement PDFs using Tesseract

Supported banks:
- Citibank
- HSBC
- OCBC

Only credit card statements are supported (for now)

## Install
Install dependencies using [Homebrew](https://brew.sh/)
```bash
brew bundle
```

Clone the repo
```bash
git clone https://github.com/benjamin-awd/monopoly.git
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

## Features
Monopoly can be run on Google Cloud as a scheduled Cloud Run job.

Current implementation:

![Screenshot](docs/monopoly_gcp.png)
