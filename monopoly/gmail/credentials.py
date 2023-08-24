from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from google.cloud import secretmanager
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from monopoly.config import settings

if TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1.resources import GmailResource


logger = logging.getLogger(__name__)


def get_credentials(secret_id=settings.secret_id, version_id="latest"):
    scopes = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.settings.basic",
        "https://www.googleapis.com/auth/gmail.labels",
    ]

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{settings.project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)

    credentials = Credentials.from_authorized_user_info(
        info=json.loads(response.payload.data), scopes=scopes
    )
    return credentials


def get_gmail_service() -> GmailResource:
    credentials = get_credentials()

    try:
        service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
        return service

    except Exception as err:
        logger.error(err)
        raise err
