from dataclasses import Field, fields
from typing import Type

from monopoly.constants import EncryptionIdentifier, MetadataIdentifier
from monopoly.pdf import PdfParser

from .base import BankBase
from .citibank import Citibank
from .dbs import Dbs
from .hsbc import Hsbc
from .ocbc import Ocbc
from .standard_chartered import StandardChartered

banks: list[Type[BankBase]] = [Citibank, Dbs, Hsbc, Ocbc, StandardChartered]


def auto_detect_bank(file_path: str) -> BankBase:
    """
    Reads the encryption metadata or actual metadata (if the PDF is not encrypted),
    and checks for a bank based on unique identifiers.
    """
    parser = PdfParser(file_path)
    for bank in banks:
        metadata = bank.get_identifier(parser)

        if is_bank_identified(metadata, bank):
            return bank(file_path=parser.file_path, parser=parser)

    raise ValueError(
        f"Could not find a bank for {parser.file_path}."
        f"This may be due a bank PDF update, leading to obsolete identifiers."
        f"To get around this, create a manual instance of the bank class."
    )


def is_bank_identified(metadata, bank: Type[BankBase]) -> bool:
    if bank.identifiers:
        for identifier in bank.identifiers:
            if all(
                check_identifier_field(field, metadata, identifier)
                for field in fields(metadata)
            ):
                return True

    return False


def check_identifier_field(
    field: Field,
    metadata: EncryptionIdentifier | MetadataIdentifier,
    identifier: EncryptionIdentifier | MetadataIdentifier,
):
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
