import os
import tempfile
from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from monopoly.bank import Statement
from monopoly.banks import Ocbc
from monopoly.statement import Transaction


def test_ocbc_write_to_local_csv(ocbc: Ocbc, statement: Statement):
    transformed_df = pd.DataFrame(
        [
            Transaction("2024-01-12", "FAIRPRICE FINEST", 18.49),
            Transaction("2023-12-28", "DA PAOLO GASTRONOMIA", 19.69),
        ]
    )
    statement.statement_date = datetime(2999, 1, 1)
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        csv_file_path = temp_file.name
        ocbc.load(df=transformed_df, statement=statement, csv_file_path=csv_file_path)

        local_df = pd.read_csv(os.path.join(csv_file_path))
        assert_frame_equal(transformed_df, local_df)
