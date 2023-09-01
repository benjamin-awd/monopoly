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
    bank_name = bank.bank_name
    account_name = bank.account_name
    year = bank.statement.statement_date.year
    month = bank.statement.statement_date.month

    filename = f"{bank_name}-{account_name}-{year}-{month:02d}.csv"

    if format_type == "blob":
        return (
            f"bank_name={bank_name}/"
            f"account_name={account_name}/"
            f"year={year}/"
            f"month={month}/"
            f"{filename}"
        )

    if format_type == "file":
        return filename

    raise ValueError("Invalid format_type")
