import logging

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


def generate_name(format_type: str, pdf):
    if format_type == "blob":
        return (
            f"bank={pdf.bank}/"
            f"account_name={pdf.account_name}/"
            f"year={pdf.statement_date.year}/"
            f"month={pdf.statement_date.month}/"
            f"{pdf.filename}"
        )
    if format_type == "file":
        return (
            f"{pdf.bank}-"
            f"{pdf.account_name}-"
            f"{pdf.statement_date.year}-"
            f"{pdf.statement_date.month:02d}.csv"
        )
    else:
        raise ValueError("Invalid format_type")
