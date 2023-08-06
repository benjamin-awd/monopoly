from datetime import datetime

import pandas as pd

from monopoly.banks.ocbc import OCBC
from monopoly.constants import AMOUNT, DATE, DESCRIPTION


def test_ocbc_transform():
    pdf = OCBC(file_path="tests/ocbc_365.pdf")
    statement_date = datetime.strptime("2024-01-01", "%Y-%m-%d")

    input_data = pd.DataFrame(
        [
            {
                DATE: "12/01",
                DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                AMOUNT: "18.49",
            },
            {
                DATE: "28/12",
                DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                AMOUNT: "19.69",
            },
        ]
    )

    df = pdf._transform_dates(input_data, statement_date)

    assert str(df.loc[0][DATE])[:10] == "2024-01-12"
    assert str(df.loc[1][DATE])[:10] == "2023-12-28"
