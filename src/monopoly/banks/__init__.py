import logging
from typing import Type

from ..examples.example_bank import ExampleBank
from .base import BankBase
from .citibank import Citibank
from .dbs import Dbs
from .hsbc import Hsbc
from .maybank import Maybank
from .ocbc import Ocbc
from .standard_chartered import StandardChartered

banks: list[Type[BankBase]] = [
    Citibank,
    Dbs,
    ExampleBank,
    Hsbc,
    Maybank,
    Ocbc,
    StandardChartered,
]

logger = logging.getLogger(__name__)
