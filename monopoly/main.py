import logging
import re

from monopoly.banks import Hsbc, Ocbc
from monopoly.constants import EmailSubjectRegex
from monopoly.gmail import Gmail, Message
from monopoly.processor import StatementProcessor

logger = logging.getLogger(__name__)


def main():
    """
    Entrypoint for Cloud Run function that extracts bank statement,
    transforms it, then loads it to disk or cloud
    """
    logger.info("Beginning bank statement extraction")

    messages: list[Message] = Gmail().get_emails()

    banks = {EmailSubjectRegex.OCBC: Ocbc, EmailSubjectRegex.HSBC: Hsbc}

    for message in messages:
        process_bank_statement(message, banks)


def process_bank_statement(message: Message, banks: dict):
    """
    Process a bank statement using the provided bank class.

    If an error occurs, the statement is removed from disk
    """
    subject = message.subject

    for bank_regex_pattern, bank_class in banks.items():
        if re.search(bank_regex_pattern, subject):
            attachment = message.get_attachment()

            with message.save(attachment) as file:
                processor: StatementProcessor = bank_class(file_path=file)
                pages = processor.get_pages()
                statement = processor.extract(pages)
                transformed_df = processor.transform(statement)
                processor.load(transformed_df, statement, upload_to_cloud=True)

                message.mark_as_read()


if __name__ == "__main__":
    main()
