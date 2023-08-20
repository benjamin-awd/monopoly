from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING

from google.cloud import secretmanager
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1.resources import GmailResource

logger = logging.getLogger(__name__)


def get_credentials(secret_id="monopoly-gmail-token", version_id="latest"):
    scopes = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.settings.basic",
        "https://www.googleapis.com/auth/gmail.labels",
    ]

    project_id = os.environ.get("PROJECT_ID")

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)

    credentials = Credentials.from_authorized_user_info(
        info=json.loads(response.payload.data), scopes=scopes
    )
    return credentials


def get_gmail_service() -> GmailResource:
    credentials = get_credentials()

    try:
        service = build("gmail", "v1", credentials=credentials)
        return service

    except Exception as err:
        logger.error(err)
        raise err


def set_up_gmail_push_notifications():
    pubsub_topic = os.environ.get("PUBSUB_TOPIC")
    project_id = os.environ.get("PROJECT_ID")
    gmail_address = os.environ.get("GMAIL_ADDRESS")

    service = get_gmail_service()
    request_body = {
        "labelIds": ["INBOX"],
        "topicName": f"projects/{project_id}/topics/{pubsub_topic}",
    }

    return (
        service.users()
        .watch(userId=gmail_address, body=request_body)
        .execute()
    )


if __name__ == "__main__":
    set_up_gmail_push_notifications()
