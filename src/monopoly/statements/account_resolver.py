"""Account resolution: which account/card each line of a statement belongs to."""

import re
from bisect import bisect_right
from operator import attrgetter
from typing import NamedTuple

from monopoly.config import StatementConfig
from monopoly.pdf import PdfPage

ACCOUNT_LAST_N = 4  # number of trailing account/card digits stamped onto transactions


def extract_last4(account_token: str | None) -> str | None:
    """
    Derive the last 4 digits from a matched account/card number token.

    Masked tokens are fine because only trailing digits matter:
    "4417 88XX XXXX 2031" -> "2031", "098-7-654321" -> "4321". Returns None when
    fewer than 4 digits are present (nothing meaningful to stamp).
    """
    if account_token is None:
        return None
    digits = re.sub(r"\D", "", account_token)
    return digits[-ACCOUNT_LAST_N:] if len(digits) >= ACCOUNT_LAST_N else None


class AccountHeader(NamedTuple):
    """An account/card header line: where it is, and the last 4 digits it opens a section for."""

    position: tuple[int, int]  # (page, line)
    last4: str


class AccountResolver:
    """
    Resolves each line's account from `config.account_pattern` matches.

    Each match opens a section; a line takes the nearest header at or above it,
    or the first account if it precedes them all.
    """

    def __init__(self, pages: list[PdfPage], config: StatementConfig):
        self.headers: list[AccountHeader] = []  # in reading order
        if (pattern := config.account_pattern) is None:
            return
        for page_num, page in enumerate(pages):
            for line_num, line in enumerate(page.lines):
                if not (match := pattern.search(line)):
                    continue
                if last4 := extract_last4(match["account"]):
                    self.headers.append(AccountHeader((page_num, line_num), last4))

    @property
    def first(self) -> str | None:
        """The statement's first account, or None if not configured/found."""
        return self.headers[0].last4 if self.headers else None

    def at(self, page_num: int, line_num: int) -> str | None:
        """Return the account of the section a line is in."""
        idx = bisect_right(self.headers, (page_num, line_num), key=attrgetter("position"))
        return self.headers[idx - 1].last4 if idx else self.first
