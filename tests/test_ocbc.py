import pandas as pd

from monopoly.banks.ocbc import OCBC
from monopoly.constants import AMOUNT, DATE, DESCRIPTION


def test_ocbc_unprotected_pdf():
    pdf = OCBC(file_path="tests/ocbc_365.pdf")
    pdf.extract()

    expected_data = pd.DataFrame(
        [
            {
                DATE: "12/06",
                DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                AMOUNT: "18.49",
            },
            {
                DATE: "12/06",
                DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                AMOUNT: "19.69",
            },
        ]
    )

    assert pdf.df.to_dict() == expected_data.to_dict()
