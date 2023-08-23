from monopoly.config import settings
from monopoly.gmail.attachment import Attachment

trusted_user_emails = ["trusted_user@gmail.com"]


def test_trusted_user(monkeypatch, attachment: Attachment):
    trusted_message = {
        "payload": {
            "headers": [
                {"name": "From", "value": "Mr Miyagi <trusted_user@gmail.com>"},
            ]
        }
    }
    monkeypatch.setattr(settings, "trusted_user_emails", trusted_user_emails)

    result = attachment._check_trusted_user(trusted_message)
    assert result == "trusted"


def test_untrusted_user(monkeypatch, attachment: Attachment):
    untrusted_message = {
        "payload": {
            "headers": [
                {"name": "From", "value": "Joe <koby@layoffs.com>"},
            ]
        }
    }
    monkeypatch.setattr(settings, "trusted_user_emails", trusted_user_emails)

    result = attachment._check_trusted_user(untrusted_message)
    assert result == "not trusted"
