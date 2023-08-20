from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from google.cloud import storage

if TYPE_CHECKING:
    from monopoly.pdf import Statement


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


def generate_name(format_type: str, statement: Statement) -> str:
    if format_type == "blob":
        return (
            f"bank={statement.bank}/"
            f"account_name={statement.account_name}/"
            f"year={statement.date.year}/"
            f"month={statement.date.month}/"
            f"{statement.filename}"
        )
    if format_type == "file":
        return (
            f"{statement.bank}-"
            f"{statement.account_name}-"
            f"{statement.date.year}-"
            f"{statement.date.month:02d}.csv"
        )
    else:
        raise ValueError("Invalid format_type")
