import logging

from .amex import Amex
from .bank_of_america import BankOfAmerica
from .base import BankBase
from .chase import Chase
from .citibank import Citibank
from .dbs import Dbs
from .detector import BankDetector
from .example_bank import ExampleBank
from .hsbc import Hsbc
from .maybank import Maybank
from .ocbc import Ocbc
from .standard_chartered import StandardChartered
from .trust import Trust
from .uob import Uob
from .zkb import ZurcherKantonalBank

banks: list[type["BankBase"]] = [
    Amex,
    BankOfAmerica,
    Chase,
    Citibank,
    Dbs,
    ExampleBank,
    Hsbc,
    Maybank,
    Ocbc,
    StandardChartered,
    Uob,
    ZurcherKantonalBank,
    Trust,
]

logger = logging.getLogger(__name__)

__all__ = ["BankDetector", "BankBase"] + [bank.__name__ for bank in banks]
