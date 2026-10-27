"""Currency resolution: which currency each line of a multi-currency statement is in."""

import logging
from bisect import bisect_right
from operator import attrgetter
from typing import NamedTuple

from monopoly.config import StatementConfig
from monopoly.pdf import PdfPage

logger = logging.getLogger(__name__)

ISO_CODE_LENGTH = 3

# Currency names as statements spell them in section headers, to ISO 4217 codes.
CURRENCY_NAMES = {
    "AUSTRALIAN DOLLAR": "AUD",
    "CANADIAN DOLLAR": "CAD",
    # offshore renminbi: not ISO 4217 (which only has CNY), but what DBS's multi-currency account holds
    "CHINESE RENMINBI": "CNH",
    "CHINESE YUAN": "CNH",
    "DANISH KRONE": "DKK",
    "EURO": "EUR",
    "HONG KONG DOLLAR": "HKD",
    "JAPANESE YEN": "JPY",
    "NEW ZEALAND DOLLAR": "NZD",
    "NORWEGIAN KRONE": "NOK",
    "POUND STERLING": "GBP",
    "SINGAPORE DOLLAR": "SGD",
    "STERLING POUND": "GBP",
    "SWEDISH KRONA": "SEK",
    "SWISS FRANC": "CHF",
    "THAI BAHT": "THB",
    "UNITED STATES DOLLAR": "USD",
}


def to_currency_code(token: str | None) -> str | None:
    """Return the ISO 4217 code a header's currency token names: a code as-is, a known name mapped, else None."""
    if token is None:
        return None
    text = " ".join(token.upper().split())
    if len(text) == ISO_CODE_LENGTH and text.isalpha():
        return text
    return CURRENCY_NAMES.get(text)


class CurrencyHeader(NamedTuple):
    """A currency section header line: where it is, and the currency it opens a section in."""

    position: tuple[int, int]  # (page, line)
    currency: str | None  # None for a currency name not in CURRENCY_NAMES


class CurrencyResolver:
    """
    Resolves each line's currency from `config.currency_pattern` matches.

    A multi-currency account prints one section per currency (DBS: "CURRENCY: UNITED STATES DOLLAR"). Each
    match opens a section; a line takes the nearest header at or above it, or the config's `currency` if it
    precedes them all (or none is configured or found). A header naming an unknown currency still opens a
    section, in currency None, so its rows aren't mislabelled with the previous section's currency.
    """

    def __init__(self, pages: list[PdfPage], config: StatementConfig):
        self.default = config.currency
        self.headers: list[CurrencyHeader] = []  # in reading order
        if (pattern := config.currency_pattern) is None:
            return
        for page_num, page in enumerate(pages):
            for line_num, line in enumerate(page.lines):
                if not (match := pattern.search(line)):
                    continue
                code = to_currency_code(match["currency"])
                if code is None:
                    logger.warning(
                        "Unknown currency %r: its section's transactions have no currency", match["currency"]
                    )
                self.headers.append(CurrencyHeader((page_num, line_num), code))

    def at(self, page_num: int, line_num: int) -> str | None:
        """Return the currency of the section a line is in."""
        idx = bisect_right(self.headers, (page_num, line_num), key=attrgetter("position"))
        return self.headers[idx - 1].currency if idx else self.default
