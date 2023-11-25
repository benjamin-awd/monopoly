import logging
from functools import wraps

import pytest

logger = logging.getLogger(__name__)


def skip_if_encrypted(func=None):
    """Helper function to skip tests if files are not unlocked with `git-crypt`"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with open("tests/integration/banks/.gc_check") as f:
                contents = f.read()
                if contents != "unlocked":
                    raise ValueError("Invalid contents")
        except UnicodeDecodeError as err:
            logger.warning(err)
            pytest.skip(
                "Test requires decrypted files. "
                "Please run 'git-crypt unlock <KEYFILE>'"
            )
        return func(*args, **kwargs)

    return wrapper if func else skip_if_encrypted
