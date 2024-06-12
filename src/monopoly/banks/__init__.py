import logging
from dataclasses import Field, fields
from itertools import product
from typing import Type

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier

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


class UnsupportedBankError(Exception):
    """Raised when a processor cannot be found for a specific bank"""


def detect_bank(
    metadata_items: list[EncryptionIdentifier | MetadataIdentifier],
) -> Type[BankBase] | None:
    """
    Reads the encryption metadata or actual metadata (if the PDF is not encrypted),
    and checks for a bank based on unique identifiers.
    """
    for bank in banks:
        if is_bank_identified(metadata_items, bank):
            return bank
    return None


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
        # Only compare matching identifier types
        if type(metadata) is not type(identifier):
            continue

        logger.debug(
            "Checking if PDF %s matches %s %s",
            metadata.__class__.__name__,
            bank.__name__,
            identifier,
        )

        if all(
            check_matching_field(field, metadata, identifier)
            for field in fields(metadata)
        ):
            logger.debug("Identified statement bank: %s", bank.__name__)
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
    field_value = getattr(metadata, field.name)
    identifier_value = getattr(identifier, field.name)

    # if identifier is not set, we assume a match
    # this means only the identifiers in the bank
    # class need to be matched.
    if not identifier_value:
        return True

    # allow for partial string matching
    # since '' in a string always is true
    # add another condition to filter out blank strings
    partial_string_match = (
        isinstance(field.type(), str) and identifier_value in field_value
    )

    # other types should match exactly
    full_match = identifier_value == field_value

    if any([partial_string_match, full_match]):
        logger.debug(
            "Match found for field `%s` : '%s' - '%s'",
            field.name,
            identifier_value,
            field_value,
        )
        return True

    return False
