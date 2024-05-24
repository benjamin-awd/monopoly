import logging
from dataclasses import Field, fields
from itertools import product
from typing import Type

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier

from ..examples.example_bank import ExampleBankProcessor
from .base import BankBase
from .citibank import Citibank
from .dbs import Dbs
from .hsbc import Hsbc
from .ocbc import Ocbc
from .standard_chartered import StandardChartered

banks: list[Type[BankBase]] = [
    Citibank,
    Dbs,
    ExampleBankProcessor,
    Hsbc,
    Ocbc,
    StandardChartered,
]

logger = logging.getLogger(__name__)


class UnsupportedBankError(Exception):
    """Raised when a processor cannot be found for a specific bank"""


def detect_bank(
    metadata_items: list[EncryptionIdentifier | MetadataIdentifier],
) -> Type[BankBase]:
    """
    Reads the encryption metadata or actual metadata (if the PDF is not encrypted),
    and checks for a bank based on unique identifiers.
    """
    for bank in banks:
        if is_bank_identified(metadata_items, bank):
            return bank

    raise UnsupportedBankError("This bank is currently not supported")


def is_bank_identified(
    metadata_items: list[EncryptionIdentifier | MetadataIdentifier],
    bank: Type[BankBase],
) -> bool:
    """
    Checks if a bank is identified based on a list of metadata items.
    """
    for identifier, metadata in product(
        bank.identifiers, metadata_items
    ):  # type: ignore
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
            logger.debug("Match found for bank %s", bank.__name__)
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
    if type(metadata) is not type(identifier):
        return False

    field_value = getattr(metadata, field.name)
    identifier_value = getattr(identifier, field.name)

    # allow for partial string matching
    partial_string_match = (
        isinstance(field.type(), str) and identifier_value in field_value
    )

    # other types should match exactly
    full_match = identifier_value == field_value

    if any([partial_string_match, full_match]):
        logger.debug("Match: %s - %s", identifier_value, field_value)
        return True

    return False
