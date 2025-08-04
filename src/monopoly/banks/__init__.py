import logging

from .amex import Amex
from .bank_of_america import BankOfAmerica
from .base import BankBase
from .bmo import BankOfMontreal
from .canadian_tire import CanadianTire
from .capitalone import CapitalOneCanada
from .chase import Chase
from .cibc import CIBC
from .citibank import Citibank
from .dbs import Dbs
from .detector import BankDetector
from .example_bank import ExampleBank
from .hsbc import Hsbc
from .maybank import Maybank
from .ocbc import Ocbc
from .rbc import RoyalBankOfCanada
from .scotiabank import Scotiabank
from .standard_chartered import StandardChartered
from .td_canada_trust import TDCanadaTrust
from .trust import Trust
from .uob import Uob
from .zkb import ZurcherKantonalBank

banks: list[type["BankBase"]] = [
    Amex,
    BankOfAmerica,
    BankOfMontreal,
    CanadianTire,
    CapitalOneCanada,
    Chase,
    CIBC,
    Citibank,
    Dbs,
    ExampleBank,
    Hsbc,
    Maybank,
    Ocbc,
    Scotiabank,
    StandardChartered,
    Uob,
    ZurcherKantonalBank,
    Trust,
    TDCanadaTrust,
    RoyalBankOfCanada,
]

logger = logging.getLogger(__name__)

__all__ = ["BankDetector", "BankBase"] + [bank.__name__ for bank in banks]
