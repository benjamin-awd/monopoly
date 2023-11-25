import logging
from dataclasses import Field, fields
from itertools import product
from pathlib import Path
from typing import Type

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.pdf import PdfParser

from .base import BankBase
from .citibank import Citibank
from .dbs import Dbs
from .example_bank import ExampleBank
from .hsbc import Hsbc
from .ocbc import Ocbc
from .standard_chartered import StandardChartered

banks: list[Type[BankBase]] = [
    Citibank,
    Dbs,
    ExampleBank,
    Hsbc,
    Ocbc,
    StandardChartered,
]


logger = logging.getLogger(__name__)


def auto_detect_bank(file_path: Path) -> BankBase:
    """
    Reads the encryption metadata or actual metadata (if the PDF is not encrypted),
    and checks for a bank based on unique identifiers.
    """
    parser = PdfParser(file_path)
    for bank in banks:
        metadata_items = bank.get_identifiers(parser)
        if is_bank_identified(metadata_items, bank):
            return bank(file_path=parser.file_path, parser=parser)

    raise ValueError(f"Could not find a bank for {parser.file_path}")


def is_bank_identified(
    metadata_items: list[EncryptionIdentifier | MetadataIdentifier],
    bank: Type[BankBase],
) -> bool:
    """
    Checks if a bank is identified based on a list of metadata items.
    """
    for identifier, metadata in product(bank.identifiers, metadata_items):
        logger.debug(
            "Comparing bank %s identifier %s against PDF metadata %s",
            bank.__name__,
            identifier,
            metadata,
        )
        if all(
            check_matching_field(field, metadata, identifier)
            for field in fields(metadata)
        ):
            return True
    return False


def check_matching_field(
    field: Field,
    metadata: EncryptionIdentifier | MetadataIdentifier,
    identifier: EncryptionIdentifier | MetadataIdentifier,
) -> bool:
    """
    Checks if a field in the metadata matches the corresponding identifier field.
    """
    # Only compare matching identifier types
    if type(metadata) is type(identifier):
        field_value = getattr(metadata, field.name)
        identifier_value = getattr(identifier, field.name)

        # allow for partial string matching
        if isinstance(field.type(), str):
            return identifier_value in field_value

        # otherwise check that values match exactly
        return identifier_value == field_value
    return False
