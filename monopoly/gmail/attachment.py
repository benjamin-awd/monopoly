from __future__ import annotations

import contextlib
import logging
import os
from base64 import urlsafe_b64decode
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from monopoly.gmail.credentials import get_gmail_service

if TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1.resources import GmailResource

logger = logging.getLogger(__name__)


# pylint: disable=no-member
class Attachment:
    def __init__(
        self,
        name: str = None,
        file_byte_string: bytes = None,
        gmail_service: GmailResource = None,
    ):
        if not gmail_service:
            self.gmail_service = get_gmail_service()

        self.name = name
        self.file_byte_string = file_byte_string

    @staticmethod
    @contextlib.contextmanager
    def persist_attachment_to_disk(attachment: Attachment) -> TemporaryDirectory:
        temp_dir = TemporaryDirectory()

        temp_file_path = os.path.join(temp_dir.name, attachment.name)
        with open(temp_file_path, "wb") as file:
            file.write(attachment.file_byte_string)

        yield temp_file_path

    def get_latest_attachment(self) -> Attachment:
        service = self.gmail_service
        message = self.get_latest_email()
        part = self._get_attachment_part(message)
        filename = part["filename"]

        if self._check_trusted_user(message) == "trusted":
            file_byte_string = self._get_attachment_byte_string(
                part, service, message["id"]
            )

        return Attachment(
            name=filename,
            file_byte_string=file_byte_string,
            gmail_service=self.gmail_service,
        )

    def get_latest_email(self) -> dict:
        emails = (
            self.gmail_service.users()
            .messages()
            .list(userId="me")
            .execute()
            .get("messages")
        )

        latest_email_id = emails[0]["id"]

        message = (
            self.gmail_service.users()
            .messages()
            .get(userId="me", id=latest_email_id)
            .execute()
        )

        return message

    @staticmethod
    def _get_attachment_byte_string(part, service: GmailResource, latest_email_id: str):
        att_id = part["body"]["attachmentId"]
        att = (
            service.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=latest_email_id, id=att_id)
            .execute()
        )
        data = att["data"]

        return urlsafe_b64decode(data.encode("utf-8-sig"))

    @staticmethod
    def _get_attachment_part(message: dict) -> dict:
        """Returns the attachment part with the filename,
        and attachmentId
        """
        for part in message["payload"]["parts"]:
            if part["filename"]:
                return part
        return None

    @staticmethod
    def _check_trusted_user(message: dict) -> str:
        """Check if user is trusted"""
        for item in message["payload"]["headers"]:
            if item["name"] == "From":
                if "<benjamindornel@gmail.com>" in item["value"]:
                    return "trusted"

        logger.info("No trusted user found")
        return "not trusted"
