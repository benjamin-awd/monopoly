from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from monopoly.config import settings
from monopoly.gmail.credentials import get_gmail_service

if TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1.resources import GmailResource

logger = logging.getLogger(__name__)


def set_up_gmail_push_notifications():
    service: GmailResource = get_gmail_service()
    request_body = {
        "labelIds": ["INBOX"],
        "topicName": f"projects/{settings.project_id}/topics/{settings.pubsub_topic}",
    }

    # pylint: disable=E1101
    return (
        service.users()
        .watch(userId=settings.gmail_address, body=request_body)
        .execute()
    )


if __name__ == "__main__":
    set_up_gmail_push_notifications()
