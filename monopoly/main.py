import logging

from monopoly.banks.ocbc import OCBC
from monopoly.config import settings
from monopoly.constants import OCBC_365
from monopoly.gmail import Gmail, Message

logger = logging.getLogger(__name__)


def main(gmail=Gmail()):
    """
    Entrypoint for Cloud Run function that extracts bank statement,
    transforms it, then loads it to disk or cloud

    If an error occurs, the statement is removed from disk
    """
    logger.info("Beginning bank statement extraction")

    messages: list[Message] = gmail.get_emails()

    for message in messages:
        attachment = message.get_attachment()

        with message.save(attachment) as file:
            if attachment.filename.startswith(OCBC_365):
                ocbc = OCBC(file_path=file, password=settings.ocbc_pdf_password)

                raw_df = ocbc.extract()
                transformed_df = ocbc.transform(raw_df)
                ocbc.load(transformed_df, upload_to_cloud=True)

        message.mark_as_read()


if __name__ == "__main__":
    main()
