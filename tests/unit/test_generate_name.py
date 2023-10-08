import uuid
from datetime import datetime
from unittest import mock

from monopoly.helpers.generate_name import generate_name
from monopoly.processor import StatementProcessor


def test_generate_blob_name(processor: StatementProcessor):
    with mock.patch.object(
        uuid.UUID, "hex", new_callable=mock.PropertyMock
    ) as mock_uuid:
        mock_uuid.return_value = "12345foo"

        statement_date = datetime(2023, 8, 1)
        expected_blob_name = (
            "bank_name=ocbc/"
            "account_type=credit/"
            "year=2023/"
            "month=8/"
            "ocbc-credit-2023-08-12345foo.csv"
        )

        actual_blob_name = generate_name(
            "blob", processor.statement_config, statement_date
        )
        assert expected_blob_name == actual_blob_name


def test_generate_file_name(processor: StatementProcessor):
    statement_date = datetime(2023, 8, 1)
    expected_file_name = "ocbc-credit-2023-08.csv"

    actual_file_name = generate_name("file", processor.statement_config, statement_date)

    assert expected_file_name == actual_file_name
