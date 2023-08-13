import logging

import google.cloud.storage as storage

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
