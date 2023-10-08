from monopoly.gmail import Message

trusted_user_emails = ["trusted_user@gmail.com"]


def test_trusted_user(message: Message):
    trusted_message = {
        "headers": [
            {"name": "From", "value": "Mr Miyagi <trusted_user@gmail.com>"},
        ]
    }
    message.payload = trusted_message
    message.trusted_user_emails = trusted_user_emails

    assert message.from_trusted_user


def test_untrusted_user(message: Message):
    untrusted_message = {
        "headers": [
            {"name": "From", "value": "Joe <koby@layoffs.com>"},
        ]
    }
    message.payload = untrusted_message
    message.trusted_user_emails = trusted_user_emails

    assert not message.from_trusted_user
