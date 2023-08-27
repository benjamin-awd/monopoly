class MultipleAttachmentsError(Exception):
    """Raise when an email has more than one attachment"""


class UntrustedUserError(Exception):
    """Raise when email received from an untrusted user"""


class NoEmailsFoundError(Exception):
    """Raise when a query returns no emails"""
