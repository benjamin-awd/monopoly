import os
from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.banks.ocbc import OCBC
from monopoly.constants import AMOUNT, DATE, DESCRIPTION, ROOT_DIR


def test_ocbc_write_to_local_csv():
    ocbc = OCBC(file_path="tests/ocbc_365.pdf")

    ocbc.statement_date = datetime.strptime("2024-01-01", "%Y-%m-%d")

    transformed_df = pd.DataFrame(
        [
            {
                DATE: "2024-01-12",
                DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
                AMOUNT: 18.49,
            },
            {
                DATE: "2023-12-28",
                DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
                AMOUNT: 19.69,
            },
        ]
    )

    ocbc.load(transformed_df)

    local_df = pd.read_csv(
        os.path.join(ROOT_DIR, "output", "OCBC-365-2024-01.csv")
    )
    assert_frame_equal(transformed_df, local_df, check_dtype=False)
