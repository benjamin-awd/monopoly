import contextlib
import logging
import os
from tempfile import TemporaryDirectory

from monopoly.banks.ocbc import OCBC
from monopoly.config import settings
from monopoly.constants import OCBC_365
from monopoly.gmail.extract import Attachment, get_latest_email_attachment

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def persist_attachment_to_disk(attachment: Attachment) -> TemporaryDirectory:
    temp_dir = TemporaryDirectory()

    temp_file_path = os.path.join(temp_dir.name, attachment.name)
    with open(temp_file_path, "wb") as file:
        file.write(attachment.file_byte_string)

    yield temp_file_path


def main():
    """
    Entrypoint for Cloud Run function that extracts bank statement,
    transforms it, then loads it to disk or cloud

    If an error occurs, the statement is removed from disk
    """
    attachment: Attachment = get_latest_email_attachment()

    with persist_attachment_to_disk(attachment) as file_path:
        if attachment.name.startswith(OCBC_365):
            ocbc = OCBC(file_path=file_path, password=settings.ocbc_pdf_password)

            raw_df = ocbc.extract()
            transformed_df = ocbc.transform(raw_df)
            ocbc.load(transformed_df, upload_to_cloud=False)

            logger.info("Successfully uploaded files to bucket")


if __name__ == "__main__":
    main()
