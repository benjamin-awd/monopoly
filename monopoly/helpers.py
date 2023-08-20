import logging
from datetime import datetime

from google.cloud import storage

logger = logging.getLogger(__name__)


def upload_to_google_cloud_storage(
    client: storage.Client,
    source_filename: str,
    bucket_name: str,
    blob_name: str,
) -> None:

    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    logger.info(f"Attempting to upload to 'gs://{bucket_name}/{blob_name}'")
    blob.upload_from_filename(source_filename)


def generate_blob_name(
    bank: str, account_name: str, statement_date: datetime, filename: str
) -> str:
    return (
        f"bank={bank}/"
        f"account_name={account_name}/"
        f"year={statement_date.year}/"
        f"month={statement_date.month}/"
        f"{filename}"
    )


def generate_file_name(bank: str, account_name: str, statement_date: datetime) -> str:
    return (
        f"{bank}-"
        f"{account_name}-"
        f"{statement_date.year}-"
        f"{statement_date.month:02d}.csv"
    )
