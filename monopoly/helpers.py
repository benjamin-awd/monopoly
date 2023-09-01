from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from google.cloud import storage

if TYPE_CHECKING:
    from monopoly.banks.bank import Bank


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


def generate_name(format_type: str, bank: Bank) -> str:
    if format_type == "blob":
        return (
            f"bank={bank.bank}/"
            f"account_name={bank.account_name}/"
            f"year={bank.statement.statement_date.year}/"
            f"month={bank.statement.statement_date.month}/"
            f"statement.csv"
        )
    if format_type == "file":
        return (
            f"{bank.bank}-"
            f"{bank.account_name}-"
            f"{bank.statement.statement_date.year}-"
            f"{bank.statement.statement_date.month:02d}.csv"
        )

    raise ValueError("Invalid format_type")
