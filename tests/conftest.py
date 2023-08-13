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
    yield pdf
