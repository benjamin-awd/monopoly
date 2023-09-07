from __future__ import annotations

import logging
from datetime import datetime

from google.cloud import storage

from monopoly.banks.statement import StatementConfig

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


def generate_name(
    format_type: str, config: StatementConfig, statement_date: datetime
) -> str:
    bank_name = config.bank_name
    account_type = config.account_type
    year = statement_date.year
    month = statement_date.month

    filename = f"{bank_name}-{account_type}-{year}-{month:02d}.csv"

    if format_type == "blob":
        return (
            f"bank_name={bank_name}/"
            f"account_type={account_type}/"
            f"year={year}/"
            f"month={month}/"
            f"{filename}"
        )

    if format_type == "file":
        return filename

    raise ValueError("Invalid format_type")
