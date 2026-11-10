import logging

from .amex import Amex
from .bank_of_america import BankOfAmerica
from .base import BankBase
from .bmo import BankOfMontreal
from .canadian_tire import CanadianTire
from .capitalone import CapitalOneCanada, CapitalOneUS
from .chase import Chase
from .cibc import CIBC
from .citibank import Citibank
from .dbs import Dbs
from .detector import BankDetector
from .hdfc import Hdfc
from .hsbc import Hsbc
from .maybank import Maybank
from .ocbc import Ocbc
from .rbc import RoyalBankOfCanada
from .schwab_bank import Schwab
from .scotiabank import Scotiabank
from .standard_chartered import StandardChartered
from .td_canada_trust import TDCanadaTrust
from .trust import Trust
from .uob import Uob
from .usbank import UsBank
from .zkb import ZurcherKantonalBank

banks: list[type[BankBase]] = [
    Amex,
    BankOfAmerica,
    BankOfMontreal,
    CanadianTire,
    CapitalOneCanada,
    CapitalOneUS,
    Chase,
    CIBC,
    Citibank,
    Dbs,
    Hdfc,
    Hsbc,
    Maybank,
    Ocbc,
    RoyalBankOfCanada,
    Schwab,
    Scotiabank,
    StandardChartered,
    TDCanadaTrust,
    Trust,
    Uob,
    UsBank,
    ZurcherKantonalBank,
]

logger = logging.getLogger(__name__)


def get_bank(name: str, *, include_generic: bool = False) -> type[BankBase]:
    """
    Return the bank whose `name` matches, case-insensitively.

    Raise a LookupError naming the supported banks if nothing matches.
    `GenericBank` is excluded unless `include_generic` is set: it is not a real
    bank and must never be auto-detected.
    """
    candidates = list(banks)
    if include_generic:
        # imported here because monopoly.generic imports this package for BankBase
        from monopoly.generic import GenericBank  # noqa: PLC0415

        candidates.append(GenericBank)

    wanted = name.casefold()
    for bank in candidates:
        if bank.name.casefold() == wanted:
            return bank
    available = ", ".join(sorted(bank.name for bank in candidates))
    msg = f"{name!r} is not a supported bank. Choose from: {available}"
    raise LookupError(msg)


__all__ = ["BankDetector", "BankBase", "get_bank"] + [bank.__name__ for bank in banks]
