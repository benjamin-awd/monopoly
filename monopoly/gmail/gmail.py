from __future__ import annotations

import contextlib
import logging
import os
import sys
from base64 import urlsafe_b64decode
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from monopoly.config import settings
from monopoly.gmail.credentials import get_gmail_service
from monopoly.gmail.exceptions import (
    AttachmentNotFoundError,
    MultipleAttachmentsError,
    UntrustedUserError,
)

if TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1.resources import GmailResource

logger = logging.getLogger(__name__)


class Gmail:
    def __init__(self, gmail_service: GmailResource = None):
        if not gmail_service:
            self.gmail_service = get_gmail_service()

    def get_emails(self, query="is:unread", latest=False) -> list[Message]:
        emails: list = (
            self.gmail_service.users()
            .messages()
            .list(userId="me", q=query)
            .execute()
            .get("messages")
        )
        if not emails:
            logger.info("No emails found using query: '%s'", query)
            sys.exit(0)

        if latest:
            emails = [emails[0]]

        messages = []
        for email in emails:
            email_id = email["id"]
            logger.info("Retrieving email %s", email_id)
            message = (
                self.gmail_service.users()
                .messages()
                .get(userId="me", id=email_id)
                .execute()
            )
            messages.append(message)

        return [Message(message, self.gmail_service) for message in messages]

    def get_attachment_byte_string(self, message_id, attachment_id) -> dict:
        logger.debug("Extracting attachment byte string")
        attachment = (
            self.gmail_service.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=message_id, id=attachment_id)
            .execute()
        )
        data: bytes = urlsafe_b64decode(attachment["data"].encode("utf-8"))
        return data


class Message(Gmail):
    def __init__(self, data: dict, gmail_service: GmailResource):
        self.message_id: str | None = data.get("id")
        self.payload: dict | None = data.get("payload")
        self.gmail_service = gmail_service
        self.trusted_user_emails = settings.trusted_user_emails
        super().__init__(gmail_service)

    def get_attachment(self):
        attachment_part = self._get_attachment_part()
        logger.info("Extracting attachment '%s'", attachment_part.filename)

        if not self.from_trusted_user:
            raise UntrustedUserError("Not from trusted user")

        file_byte_string = self.get_attachment_byte_string(
            self.message_id, attachment_part.attachment_id
        )
        return MessageAttachment(attachment_part.filename, file_byte_string)

    @staticmethod
    @contextlib.contextmanager
    def save(attachment: MessageAttachment) -> TemporaryDirectory:
        """Saves attachment to a temporary directory"""
        temp_dir = TemporaryDirectory()
        temp_file_path = os.path.join(temp_dir.name, attachment.filename)

        try:
            logger.info("Writing attachment to path %s", temp_file_path)
            with open(temp_file_path, "wb") as file:
                file.write(attachment.file_byte_string)

            yield temp_file_path
        except Exception as error:
            logger.error("An error occurred while saving: %s", error)
            raise
        finally:
            temp_dir.cleanup()

    def mark_as_read(self):
        logger.info("Marking email %s as read", self.message_id)
        return (
            self.gmail_service.users()
            .messages()
            .modify(
                userId="me", id=self.message_id, body={"removeLabelIds": ["UNREAD"]}
            )
            .execute()
        )

    def _get_attachment_part(self) -> MessagePart:
        if not self.parts:
            raise AttachmentNotFoundError

        attachments = [part for part in self.parts if part.filename]
        if not attachments:
            raise AttachmentNotFoundError

        if len(attachments) > 1:
            raise MultipleAttachmentsError

        return attachments[0]

    @property
    def subject(self) -> str:
        for item in self.payload.get("headers"):
            if item["name"] == "Subject":
                return item["value"]
        raise RuntimeError("Subject could not be found")

    @property
    def parts(self) -> list[MessagePart]:
        """Return parts and nested parts"""
        if parts := self.payload.get("parts"):
            nested_parts = [
                nested_part
                for part in list(parts)
                if part.get("parts")
                for nested_part in part.get("parts")
            ]
            return [MessagePart(part) for part in parts + nested_parts]

        return None

    @property
    def from_trusted_user(self) -> bool:
        """Check if user is trusted"""
        for item in self.payload["headers"]:
            if item["name"] == "From":
                for trusted_email in self.trusted_user_emails:
                    if f"<{trusted_email}>" in item["value"]:
                        return True

        logger.info("No trusted user found")
        return False


@dataclass
class MessagePart:
    def __init__(self, data: dict):
        self._data = data
        self.part_id: str = data.get("partId")
        self.filename: str = data.get("filename")
        self.body: dict = data.get("body")

    @property
    def attachment_id(self):
        return self.body.get("attachmentId")

    def __repr__(self):
        return str(self._data)


@dataclass
class MessageAttachment:
    def __init__(self, filename, file_byte_string):
        self.filename: str = filename
        self.file_byte_string: bytes = file_byte_string

    def __repr__(self):
        return str(self.filename)
