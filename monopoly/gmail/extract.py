from __future__ import annotations

import logging
from base64 import urlsafe_b64decode
from dataclasses import dataclass
from typing import TYPE_CHECKING

from monopoly.gmail.credentials import get_gmail_service

if TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1.resources import GmailResource

logger = logging.getLogger(__name__)


@dataclass
class Attachment:
    name: str
    file_byte_string: str


def check_trusted_user(message: dict):
    for item in message["payload"]["headers"]:
        if item["name"] == "From":
            if "<benjamindornel@gmail.com>" in item["value"]:
                return "trusted"

    logger.info("Untrusted user: %s", item["value"])
    return "not trusted"


def get_latest_email(service: GmailResource) -> dict:
    emails = service.users().messages().list(userId="me").execute().get("messages")

    # Get latest email
    latest_email_id = emails[0]["id"]

    message = service.users().messages().get(userId="me", id=latest_email_id).execute()

    return message


def get_pdf_attachment(message: dict, service: GmailResource, latest_email_id: str):
    attachment = {}
    for part in message["payload"]["parts"]:
        if part["filename"]:
            filename = part["filename"]
            logger.info("Downloading email attachment")
            att_id = part["body"]["attachmentId"]
            att = (
                service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=latest_email_id, id=att_id)
                .execute()
            )
            data = att["data"]

            file_byte_string: bytes = urlsafe_b64decode(data.encode("utf-8-sig"))

            attachment = Attachment(name=filename, file_byte_string=file_byte_string)

    return attachment


def get_latest_email_attachment() -> dict:
    service = get_gmail_service()
    message = get_latest_email(service)

    if check_trusted_user(message) == "trusted":
        attachment = get_pdf_attachment(message, service, message["id"])

    return attachment
