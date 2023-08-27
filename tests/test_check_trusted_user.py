from monopoly.config import settings
from monopoly.gmail import Message

trusted_user_emails = ["trusted_user@gmail.com"]


def test_trusted_user(monkeypatch, message: Message):
    trusted_message = {
        "headers": [
            {"name": "From", "value": "Mr Miyagi <trusted_user@gmail.com>"},
        ]
    }
    message.payload = trusted_message
    monkeypatch.setattr(settings, "trusted_user_emails", trusted_user_emails)

    assert message.from_trusted_user == True


def test_untrusted_user(monkeypatch, message: Message):
    untrusted_message = {
        "headers": [
            {"name": "From", "value": "Joe <koby@layoffs.com>"},
        ]
    }
    message.payload = untrusted_message
    monkeypatch.setattr(settings, "trusted_user_emails", trusted_user_emails)

    assert message.from_trusted_user == False
