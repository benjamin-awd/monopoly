from datetime import datetime

import pytest

from monopoly.banks.ocbc import OCBC
from monopoly.pdf import PDF


@pytest.fixture(scope="session")
def ocbc():
    ocbc = OCBC()
    yield ocbc


@pytest.fixture(scope="session")
def pdf():
    pdf = PDF()
    pdf.bank = "Example Bank"
    pdf.account_name = "Savings"
    pdf.statement_date = datetime(2023, 8, 1)
    pdf.filename = "statement.csv"

    yield pdf
