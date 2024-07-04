import logging
from dataclasses import Field, fields
from typing import Type

from monopoly.constants import Identifier

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
    metadata_items: list[Identifier],
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
    metadata_items: list[Identifier],
    bank: Type[BankBase],
) -> bool:
    """
    Checks if a bank is identified based on a list of metadata items.
    """
    for grouped_identifiers in bank.identifiers:  # type: ignore
        if len(metadata_items) != len(grouped_identifiers):
            continue

        if all_identifiers_match(metadata_items, grouped_identifiers):
            logger.debug("Identified statement bank: %s", bank.__name__)
            return True

    return False


def all_identifiers_match(
    metadata_items: list[Identifier],
    grouped_identifiers: list[Identifier],
) -> bool:
    """
    Checks if all identifiers in the group match at least one metadata item.
    """
    for identifier in grouped_identifiers:
        matching_metadata = [
            metadata
            for metadata in metadata_items
            if type(metadata) is type(identifier)
        ]

        if not any(
            check_matching_identifier(metadata, identifier)
            for metadata in matching_metadata
        ):
            return False
    return True


def check_matching_identifier(
    metadata: Identifier,
    identifier: Identifier,
) -> bool:
    """
    Checks if all fields in the metadata match the corresponding identifier fields.
    """
    return all(
        check_matching_field(field, metadata, identifier) for field in fields(metadata)
    )


def check_matching_field(
    field: Field,
    metadata: Identifier,
    identifier: Identifier,
) -> bool:
    """
    Checks if a field in the metadata matches the corresponding identifier field.
    """
    field_value = getattr(metadata, field.name)
    identifier_value = getattr(identifier, field.name)

    # if identifier is empty, we assume a match
    # this means only the identifiers in the bank
    # class need to be matched.
    if not identifier_value:
        return True

    # support partial string matching
    if isinstance(field_value, str) and isinstance(identifier_value, str):
        return identifier_value in field_value and identifier_value != ""

    # if not a string, only support exact match
    return identifier_value == field_value
