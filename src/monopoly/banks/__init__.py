import logging
from typing import Type

from .base import BankBase
from .citibank import Citibank
from .dbs import Dbs
from .detector import BankDetector
from .example_bank import ExampleBank
from .hsbc import Hsbc
from .maybank import Maybank
from .ocbc import Ocbc
from .standard_chartered import StandardChartered
from .uob import Uob
from .zkb import ZurcherKantonalBank

banks: list[Type["BankBase"]] = [
    Citibank,
    Dbs,
    ExampleBank,
    Hsbc,
    Maybank,
    Ocbc,
    StandardChartered,
    Uob,
    ZurcherKantonalBank,
]

logger = logging.getLogger(__name__)

__all__ = ["BankDetector", "BankBase", *[bank.__name__ for bank in banks]]
