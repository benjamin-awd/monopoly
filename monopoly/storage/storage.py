import logging
import os

from google.cloud import storage
from pandas import DataFrame

from monopoly.constants import ROOT_DIR
from monopoly.helpers.generate_name import generate_name
from monopoly.statement import Statement


def upload_to_cloud_storage(
    source_filename: str,
    bucket_name: str,
    statement: Statement,
) -> None:
    client = storage.Client()
    logger = logging.getLogger(__name__)
    bucket = client.get_bucket(bucket_name)

    blob_name = generate_name("blob", statement.config, statement.statement_date)
    blob = bucket.blob(blob_name)

    logger.info(f"Attempting to upload to 'gs://{bucket_name}/{blob_name}'")
    blob.upload_from_filename(source_filename)
    logger.info("Uploaded to %s", blob_name)


def write_to_csv(df: DataFrame, csv_file_path: str, statement: Statement):
    logger = logging.getLogger(__name__)

    if not csv_file_path:
        filename = generate_name("file", statement.config, statement.statement_date)
        csv_file_path = os.path.join(ROOT_DIR, "output", filename)
        logger.info("Writing CSV to file path: %s", csv_file_path)

    df.to_csv(csv_file_path, index=False)

    return csv_file_path
