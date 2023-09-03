import logging

from monopoly.banks.hsbc.credit import HsbcRevolution
from monopoly.banks.ocbc.credit import Ocbc365
from monopoly.constants import HSBC_REVOLUTION, OCBC_365
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

        if OCBC_365 in message.subject:
            with message.save(attachment) as file:
                ocbc = Ocbc365(file_path=file)

                statement = ocbc.extract()
                statement_date = statement.statement_date

                raw_df = statement.to_dataframe()
                transformed_df = ocbc.transform(raw_df, statement_date)
                ocbc.load(transformed_df, statement_date, upload_to_cloud=True)

                message.mark_as_read()

        if HSBC_REVOLUTION in message.subject:
            with message.save(attachment) as file:
                hsbc = HsbcRevolution(file_path=file)

                statement = hsbc.extract()
                statement_date = statement.statement_date

                raw_df = statement.to_dataframe()
                transformed_df = hsbc.transform(raw_df, statement_date)
                hsbc.load(transformed_df, statement_date, upload_to_cloud=True)

                message.mark_as_read()


if __name__ == "__main__":
    main()
