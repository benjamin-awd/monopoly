import logging

from monopoly.banks.ocbc import OCBC
from monopoly.config import settings
from monopoly.constants import OCBC_365
from monopoly.gmail.attachment import Attachment

logger = logging.getLogger(__name__)


def main():
    """
    Entrypoint for Cloud Run function that extracts bank statement,
    transforms it, then loads it to disk or cloud

    If an error occurs, the statement is removed from disk
    """
    attachment = Attachment().get_latest_attachment()

    with attachment.save(attachment) as file_path:
        if attachment.name.startswith(OCBC_365):
            ocbc = OCBC(file_path=file_path, password=settings.ocbc_pdf_password)

            raw_df = ocbc.extract()
            transformed_df = ocbc.transform(raw_df)
            ocbc.load(transformed_df, upload_to_cloud=False)

            logger.info("Successfully uploaded files to bucket")


if __name__ == "__main__":
    main()
